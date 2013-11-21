#!/usr/bin/env python

# Dynamixel library for MX28 and MX64

# WINDOWS WARNING: For best performance, parameters of the COM Port should be set to maximum baud rate, and 1ms delay (Device Manager, COM Ports, properties, advanced)

from dxlcore import *
from dxlregisters import *

import logging
from collections import OrderedDict




class ModelRegisteringMetaclass(type):
    def __new__(cls, name, bases, attrs):
        inst=type.__new__(cls, name,bases,attrs)        
        DxlMotor.registerModel(inst.model_number,inst)        
        return inst
        



class DxlMotor(object):
    DxlModels={}
    
    def __init__(self):
        self.registers=OrderedDict()        
    
    
    @classmethod
    def registerModel(cls,model_number,model_cls):
        if model_number not in cls.DxlModels.keys():
            cls.DxlModels[model_number]=model_cls
            logging.info( "Registered Dynamixel Motor model %s (%d): "%(model_cls.model_name,model_number)+str(model_cls) )

    @classmethod
    def instantiateMotor(cls,model_number):
        if not model_number in cls.DxlModels.keys():
            raise DxlConfigurationException,"Cannot instantiate non-existing motor model %d "%(name,model_number)
        mcls=cls.DxlModels[model_number]
        return mcls()
        

        
    def getRegisterCmd(self,name):
        if not name in self.registers.keys():
            raise DxlConfigurationException,"Model %s has no register called %s"%(name,self.model_name)
        r=self.registers[name]
        if not 'r' in r.mode:
            raise DxlConfigurationException,"Register %s is not readable"%(name)
        return (r.size,[Dxl.CMD_READ_DATA,r.address,r.size])

    def setRegisterCmd(self,name,value):
        if not name in self.registers.keys():
            raise DxlConfigurationException,"Model %s has no register called %s"%(self.model_name,name)
        r=self.registers[name]
        if not 'w' in r.mode:
            raise DxlConfigurationException,"Register %s is not writable"%(name)
        if r.size!=len(value):
            raise DxlConfigurationException,"Model %s register %s has size %d: passed size %d"%(self.model_name,name,r.size,len(value))
            
        return (0,[Dxl.CMD_WRITE_DATA,r.address]+value )

    def sort(self):
        self.registers = OrderedDict( sorted(self.registers.iteritems(), key=lambda x: x[1].address) )
    
class DxlMotorAXMX(DxlMotor):
    def __init__(self):
        DxlMotor.__init__(self)

        self.registers["model_number"]=         DxlRegisterWord(0x00,'r',eeprom=True)
        self.registers["firmware"]=             DxlRegisterByte(0x02,'r',eeprom=True)
        self.registers["id"]=                   DxlRegisterByte(0x03,'rw',eeprom=True)
        self.registers["baud_rate"]=            DxlRegisterByte(0x04,'rw',eeprom=True)
        self.registers["return_delay"]=         DxlRegisterByte(0x05,'rw',eeprom=True)
        self.registers["cw_angle_limit"]=       DxlRegisterWord(0x06,'rw',eeprom=True)
        self.registers["ccw_angle_limit"]=      DxlRegisterWord(0x08,'rw',eeprom=True)
        self.registers["high_temp_limit"]=      DxlRegisterByte(0x0b,'rw',eeprom=True)
        self.registers["low_voltage_limit"]=    DxlRegisterByte(0x0c,'rw',eeprom=True)
        self.registers["high_voltage_limit"]=   DxlRegisterByte(0x0d,'rw',eeprom=True)
        self.registers["max_torque"]=           DxlRegisterWord(0x0e,'rw',eeprom=True)
        self.registers["status_return_level"]=  DxlRegisterByte(0x10,'rw',eeprom=True)
        self.registers["alarm_led"]=            DxlRegisterByte(0x11,'rw',eeprom=True)
        self.registers["alarm_shutdown"]=       DxlRegisterByte(0x12,'rw',eeprom=True)

        self.registers["torque_enable"]=        DxlRegisterByte(0x18,'rw')
        self.registers["led"]=                  DxlRegisterByte(0x19,'rw')
        
        # Here goes compliance or PID or DIP
        
        self.registers["goal_pos"]=             DxlRegisterWord(0x1E,'rw')
        self.registers["moving_speed"]=         DxlRegisterWord(0x20,'rw')
        self.registers["torque_limit"]=         DxlRegisterWord(0x22,'rw')
        self.registers["present_position"]=     DxlRegisterWord(0x24,'r')
        self.registers["present_speed"]=        DxlRegisterWord(0x26,'r')
        self.registers["present_load"]=         DxlRegisterWord(0x28,'r')

        self.registers["present_voltage"]=      DxlRegisterByte(0x2A,'r')
        self.registers["present_temp"]=         DxlRegisterByte(0x2B,'r')
        self.registers["registered"]=           DxlRegisterByte(0x2C,'r')
        self.registers["moving"]=               DxlRegisterByte(0x2E,'r')
        self.registers["lock"]=                 DxlRegisterByte(0x2F,'rw')
        self.registers["punch"]=                DxlRegisterWord(0x30,'rw')
        
        self.sort()


class DxlMotorAX12(DxlMotorAXMX):
    __metaclass__=ModelRegisteringMetaclass
    model_name="AX12"
    model_number=12
    
    def __init__(self):
        DxlMotorAXMX.__init__(self)

        self.registers["cw_compliance_margin"]= DxlRegisterByte(0x1A,'rw')
        self.registers["ccw_compliance_margin"]=DxlRegisterByte(0x1B,'rw')
        self.registers["cw_compliance_slope"]=  DxlRegisterByte(0x1C,'rw')
        self.registers["ccw_compliance_slope"]= DxlRegisterByte(0x1D,'rw')

        self.sort()
        

class DxlMotorMX28(DxlMotorAXMX):
    __metaclass__=ModelRegisteringMetaclass
    model_name="MX28"
    model_number=29

    def __init__(self):
        DxlMotorAXMX.__init__(self)

        self.registers["p_gain"]=               DxlRegisterByte(0x1A,'rw')
        self.registers["i_gain"]=               DxlRegisterByte(0x1B,'rw')
        self.registers["d_gain"]=               DxlRegisterByte(0x1C,'rw')
        
        self.sort()

class DxlMotorMX64(DxlMotorAXMX):
    __metaclass__=ModelRegisteringMetaclass
    model_name="MX64"
    model_number=310

    def __init__(self):
        DxlMotorAXMX.__init__(self)
        
        self.registers["d_gain"]=               DxlRegisterByte(0x1A,'rw')
        self.registers["i_gain"]=               DxlRegisterByte(0x1B,'rw')
        self.registers["p_gain"]=               DxlRegisterByte(0x1C,'rw')
        
        self.sort()