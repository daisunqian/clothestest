#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 2017-09-03

@author: zhouql
'''

from Comm.InnorevModbus import *
import time


class MoonsController(object):
    
    def __init__(self, port):
        # InnorevModbus.__init__(self,port)
        self.port = port
        self.MoonsHomeStatus = 0x3C     #40061
        self.MoonsPositionAddress = 0x1B
        self.MoonsStatusAddress = 0x01    #40002 -40001
        self.MoonsImmediateControlAddress = 0x7C #40125 - 40001
        self.Clear_Alarm_OP = 0xBA
        self.modbus = None
        # self.init_msg = ''
        # try:
        #     self.modbus = InnorevModbus.getInstance(port)
        #     self.init_msg = 'ok'
        # except Exception, ex:
        #     self.init_msg = 'init exception: ' + ex.message

    # 自动查找端口
    # port_list端口集合
    def auto_connect(self, port_list, subordinate=1):
        if port_list is None or len(port_list) == 0:
            return False, 'do not ports'
        for port in port_list:
            if self.modbus is not None:
                self.modbus.close()
            try:
                self.modbus = InnorevModbus.getInstance(port, True)
                if self.checkConnect(subordinate):
                    return True, port
            except Exception, ex:
                if self.modbus is not None:
                    self.modbus.close()
            finally:
                if self.modbus is not None:
                    self.modbus.close()

        return False, 'moon port connect fail'

    # 检测连接
    def checkConnect(self, subordinate=1):
        try:
            if self.modbus is None:
                self.modbus = InnorevModbus.getInstance(self.port)

            if self.modbus.InnorevOpenSerial():
                data = self.CheckHomeStatus(subordinate)
                return True
            else:
                return False
        except Exception,e:
            return False

    # 读取电机状态()
    def GetMoonsStatus(self, subordinate, count=1):
        '''
        0x0001   ---    Motor Enabled(Motor Disabled if this bit = 0)
        0x0002   ---    Sampling(for Quick Tuner)
        0x0004   ---    Drive Fault(check Alarm Code)
        0x0008   ---    In position(Motor is in position)
        0x0010   ---    Moving(Motor is moving)
        0x0020   ---    Jogging(currently in jog mode)
        0x0040   ---    Stopping(in the process of stopping from a stop command)
        0x0100   ---    Saving(parameter data is being saved)
        0x0200   ---    Alarm present(check Alarm Code)
        0x0400   ---    Homing(executing a WT command)
        0x0800   ---    Stopping(in the process of stopping from a stop command)
        0x1000   ---    Wizard running(Timing Wizard is running)
        0x2000   ---    Checking encoder(Timing Wizard is running)
        0x4000   ---    Q program is running
        0x8000   ---    Initializing(happens at power up)
        '''
        data = self.modbus.InnorevReadHodlingRegister(subordinate, self.MoonsStatusAddress, count)
        return data

    # 检测home位置
    def CheckHomeStatus(self, subordinate):
        self.clear_alarm(subordinate)
        data = self.modbus.InnorevReadHodlingRegister(subordinate, self.MoonsHomeStatus, 2)
        if((data[0] == 1 or data[1] == 1)):
            return True
        else:
            return False

    def clear_alarm(self, subordinate):
        status = self.modbus.InnorevWriteSingleRegister(subordinate, self.MoonsImmediateControlAddress, self.Clear_Alarm_OP)
        time.sleep(0.01)
        return status

    # 设置home, 回原点
    def SetMoonsHome(self, subordinate=1):
        self.clear_alarm(subordinate)
        para_list = []
        para_list.append(0x78)
        para_list.append(0x01)
        if(True == self.modbus.InnorevWriteMultipleRegister(subordinate, self.MoonsImmediateControlAddress, para_list)):
            IsInPosition = self.CheckHomeStatus(subordinate)
            while(False == IsInPosition):
                time.sleep(0.1)
                IsInPosition = self.CheckHomeStatus(subordinate)
            return True

    # 设置电机0点???
    def SetMoonsZeroPosition(self, subordinate, para_list):
        self.clear_alarm(subordinate)
        if(True == self.modbus.InnorevWriteMultipleRegister(subordinate,self.MoonsImmediateControlAddress, para_list)):
            para_list1 = []
            para_list1.append(0x98)
            para_list1.append(para_list[1])
            if(True == self.modbus.InnorevWriteMultipleRegister(subordinate,self.MoonsImmediateControlAddress, para_list1)):
                para_list2 = []
                para_list2.append(0xA5)
                para_list2.append(para_list[1])
                if(True == self.modbus.InnorevWriteMultipleRegister(subordinate,self.MoonsImmediateControlAddress, para_list1)):
                    return True
                else:
                    return False

    # 立即运动
    def SetMoonsImmediatelyMove(self, subordinate):
        self.clear_alarm(subordinate)
        return self.modbus.InnorevWriteSingleRegister(subordinate, self.MoonsImmediateControlAddress, 0x67)

    # 立即停止
    def SetMoonsImmediatelyStop(self, subordinate):
        return self.modbus.InnorevWriteSingleRegister(subordinate, self.MoonsImmediateControlAddress, 0xE1)

    # 运动到指定pose位置
    def SetMoonsPosition(self, subordinate, para_list):
        self.clear_alarm(subordinate)
        if( True == self.modbus.InnorevWriteMultipleRegister(subordinate, self.MoonsPositionAddress, para_list)):
            if(True == self.SetMoonsImmediatelyMove(subordinate)):
                return True
            else:
                return False

    # 角度转换成脉冲
    def _degreeToPosition(self, degree, ratio=1,lead=360):
        '''
        x 1 round    :     10000
          10 rounds  :     360 degree
          
        y 1 round    :     10000
          40 rounds  :     360 degree
          
        z 1 round    :     10000
          40 rounds  :     360 degree
        '''
        degree = float(degree)/lead*360
        return int(((degree * 10000) / 360)*ratio)

    # 角度(旋转)运动
    def MoveDegree(self, subordinate, position, speed, acceleration, deceleration, ratio=1):
        self.clear_alarm(subordinate)
        position = self._degreeToPosition(position,ratio)
        para_list = []
        para_list.append(acceleration)
        para_list.append(deceleration)
        para_list.append(speed)
        (var1,var2) = self.IntToHex(32, position) 
        para_list.append(var1)
        para_list.append(var2)
        number = 1
        if( True == self.SetMoonsPosition(subordinate,para_list)):
            data = self.GetMoonsStatus(subordinate)
            while(int(data[0]) < 9):
                number = number + 1
                if(number > 15):
                   break
                else:
                    time.sleep(0.1)
                    data = self.GetMoonsStatus(subordinate)
            return True
        else:
            return False

    # 直线运动
    # position 使用脉冲数据
    def MoveLine(self, subordinate, position, speed, acceleration, deceleration, ratio=1, lead=10, sync=True, timeout=30):
        self.clear_alarm(subordinate)
        para_list = self.get_para_list(position, speed, acceleration, deceleration, ratio=ratio, lead=lead)
        data = self.GetMoonsStatus(subordinate, 8)
        # print "position:", position
        # print subordinate, ":", data
        test_status = False
        if( True == self.SetMoonsPosition(subordinate,para_list)):
            data = self.GetMoonsStatus(subordinate, 8)
            # print subordinate,"->:",data
            if sync:
                st = time.time()
                # while (data[0] != 9):
                while time.time() - st <= timeout:
                    data = self.GetMoonsStatus(subordinate, 8)
                    if data[0] == 9:
                        test_status = True
                        break
                    # print subordinate, ":", data
                    time.sleep(0.1)
                    # print subordinate,":",data
                    if data[2] == 18:
                        break
            else:
                test_status = True
            return test_status
        else:
            return False

    # 停止状态，true已停止，否则在运动中
    def StopStatus(self, subordinate):
        datas = self.GetMoonsStatus(subordinate, 8)
        # print datas
        return datas[0] == 9 or datas[2] == 18

    def HexToInt(self, x, y):
        '''
        two 2-byte hex is divided to a number
        '''
        import struct
        str =struct.pack(">HH",x,y)
        tuple_int =struct.unpack(">i",str)
        return tuple_int[0]

    def IntToHex(self, nbits, number):
        '''
        a number is divided to two 2-byte hex
        '''
        return (((number + (1 << nbits)) % (1 << nbits) & 0xffff) ,((number + (1 << nbits)) % (1 << nbits) >> 16))

    # 直线运动组合下发数据,
    # postion脉冲数据
    def get_para_list(self, position, speed, acceleration, deceleration, ratio=1,lead=10):
        # position = self._degreeToPosition(position,ratio,lead)  # 屏蔽直接使用脉冲数据运动
        # print "moons position:", position
        para_list = []
        para_list.append(acceleration)
        para_list.append(deceleration)
        para_list.append(speed)
        (var1, var2) = self.IntToHex(32, position)
        para_list.append(var1)
        para_list.append(var2)
        return para_list


if __name__ == "__main__":
    asd = MoonsController("COM3")
    # print asd.checkConnect(1)
    print asd.auto_connect(["COM3"])
    # print asd.clear_alarm(2)
    # print asd.CheckHomeStatus(5)
    # print asd.GetMoonsStatus(5, 3)
    # print asd.SetMoonsImmediatelyStop(5)
    # print asd.MoveLine(2, 10000, 200, 300, 300, sync=True)
    # time.sleep(2)
    # print asd.SetMoonsImmediatelyStop(5)
    # print asd.GetMoonsStatus(5, 8)

    print asd.SetMoonsHome(2)
    # print 'home status ', asd.CheckHomeStatus(5)
    # time.sleep(3)
    #

    # if not asd.CheckHomeStatus(2):
    #     asd.SetMoonsHome(2)
    # print asd.SetMoonsHome(2)
    # time.sleep(0.1)
    # # asd.MoveLine(1,1)
    # asd.MoveLine(5,10, 100, 300, 300, 1)
    # asd.MoveLine(1, 330, 300, 300, 300, ratio=1, lead=10)
    # # asd.SetxMoonsImmediatelyStop(1)
    # print asd.GetMoonsStatus(1)