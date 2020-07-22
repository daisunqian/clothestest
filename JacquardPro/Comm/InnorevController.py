#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 2017-09-03

@author: zhouql
'''

import sys
import ConfigParser
import time
import logging
import sqlite3
import serial
import threading
import re
import pdb


class InnorevController(object):
    '''
    classdocs
    '''
    def __init__(self, port,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.1,parent=None):
        self.port = port
        self.baudrate = baudrate
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.bytesize = serial.EIGHTBITS
        self.timeout = 0.1
        self.main = None      # serial.Serial(port, baudrate, bytesize,  parity, stopbits, timeout)
        self.lock = threading.Lock()
        self.message = ''

    # 自动查找端口
    # port_list端口集合
    def auto_connect(self, port_list):
        if port_list is None or len(port_list) == 0:
            return False, 'do not ports'
        for port in port_list:
            if self.main is not None:
                self.main.close()
            try:
                self.main = serial.Serial(port, self.baudrate, self.bytesize, self.parity, self.stopbits, self.timeout)
                if self.checkConnect():
                    self.port = port
                    return True, port
                else:
                    self.main.close()
                    self.main = None
            except Exception, ex:
                if self.main is not None:
                    self.main.close()
            finally:
                if self.main is not None:
                    self.main.close()

        return False, 'io port connect fail'

    def close(self):
        self.main.close()
        self.message = 'port close'

    def __open(self):
        try:
            self.message = ''
            if self.main is not None and self.main.isOpen() is False:
                self.main.open()
        except Exception, ex:
            self.message = 'open {0} fail, {1}'.format(self.main.port, ex.message)


    """
       check the serial port is or not innorev board serial port
        @param subordinate: default,not used.just adapt style
        @return: bool:success True,failed False
    """
    def checkConnect(self,subordinate=0):
        try:
            if self.main is None:
                self.main = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits,
                                            self.timeout)
            ok,data = self.readDI()
            if ok:
                return True
            else:
                return False
        except Exception,e:
            # print "Exception%s"%(e)
            self.message = "checkConnect Exception%s"%(e)
            return False

    """
        @param value: innorev board id
        @param timeout: wait timeout.
        @return: tuple(bool,str)
                0:success True,failed False
                1:source data
    """
    def WriteID(self, value, timeout=1):
        try:
            self.lock.acquire()
            self.message = ''
            if self.main.isOpen():
                self.main.flushInput()
                command = "WriteEEPROM 0x0090 %#.2x\r"%(value)
                n=self.main.write(command)
                data = self.main.read(1000)
                starttime = time.time()
                while True:
                    n=self.main.inWaiting()
                    if(n==0):
                        break
                    if time.time()-starttime>timeout:
                        break
                    data=data+self.main.read(n)
                lst = data.split("\r\n")
                if lst[2]=="OK":
                    return True,data
                else:
                    self.message = 'WriteID data error ' + data
                    return False,data
        except Exception,e:
            self.message = "WriteID exception " + e.message
            return False,str(e)
        finally:
            self.lock.release()

    def WriteSN(self,value,timeout=1):
        try:
            self.lock.acquire()
            self.message = ''
            if self.main.isOpen():
                self.main.flushInput()
                command = "WriteSN %.4d\r"%(value)
                n=self.main.write(command)
                data = self.main.read(1000)
                starttime = time.time()
                while True:
                    n=self.main.inWaiting()
                    if(n==0):
                        break
                    if time.time()-starttime>timeout:
                        break
                    data=data+self.main.read(n)
                lst = data.split("\r\n")
                if lst[2]=="OK":
                    return True,data
                else:
                    self.message = 'WriteSN data error ' + data
                    return False,data
        except Exception,e:
            self.message = "WriteSN exception " + e.message
            return False,str(e)
        finally:
            self.lock.release()

    def analysisResultDI(self,result,index):
        try:
            num=-1
            binary = bin(int(result,16))
            if len(binary)==34:
                if index>=24:
                    num = (int(str(result),16)>>index-24+4-1)&1
                else:
                    num = (int(str(result),16)>>index+8-1)&1
            else:
                num = (int(result,16)>>index-1)&1
            return num
        except Exception,e:
            self.message = "analysisResultDI exception " + e.message
            return str(e)

    """
    @param index 1~20
          inputType 1 output,0 input
    @return num, io status. 0 is on,1 is off
            data,source data
    """
    def readSingle(self, index, inputType=0):
        if inputType:
            num = -1
            ok,data = self.readDO()
            if ok:
               return (int(data,16)>>index-1)&1,data
            else:
                return (-1, data)
        else:
            ok, data = self.readDI()
            num = self.analysisResultDI(data,index)
            return num, data
    """
    @param timeout wait for time
    @return tuple(bool, str)
            0:success True,failed False
            1:success it is board id,like "1",failed,it is source data or errormessage
            source data: like "readEEprom 0x0090\n \n0x01\nOK\n >"
    """
    def ReadID(self,timeout=1):
        try:
            self.lock.acquire()
            self.message = ''
            if self.main.isOpen() is False:
                self.__open()

            if self.main.isOpen():
                self.main.flushInput()
                command = "readEEprom 0x0090\r".encode("utf-8")
                #pdb.set_trace()
                self.main.flushOutput()
                n=self.main.write(command)
                data = self.main.read(1000)
                starttime = time.time()
                while True:
                    time.sleep(0.01)
                    n=self.main.inWaiting()
                    if(n==0):
                        break
                    if time.time()-starttime>timeout:
                        break
                    data += self.main.read(n)
                    
                lst = data.split("\r\n")
                if len(lst)==5 and lst[3]=="OK":
                    return True,lst[2]
                else:
                    self.message = 'ReadID data error ' + data
                    return False,data
        except Exception,e:
            self.message = "ReadID exception " + e.message
            print "==========readid excption=======%s\n"%str(e)
            return False,str(e),
        finally:
            self.lock.release()

    def ReadSN(self,timeout=1):
        try:
            self.lock.acquire()
            self.message = ''
            if self.main.isOpen() is False:
                self.__open()

            if self.main.isOpen() :
                self.main.flushInput()
                command = "readsn\r".encode("utf-8")
                #pdb.set_trace()
                self.main.flushOutput()
                n=self.main.write(command)
                data = self.main.read(1000)
                starttime = time.time()
                while True:
                    time.sleep(0.01)
                    n=self.main.inWaiting()
                    sys.stdout.flush()
                    if(n==0):
                        break
                    if time.time()-starttime>timeout:
                        break
                    data += self.main.read(n)
                    
                lst = data.split("\r\n")
                if (len(lst)==4 and lst[2]=="OK") or (len(lst)==5 and lst[3]=="OK") :
                    return True,lst[1] if lst[2]=="OK" else lst[2]
                else:
                    self.message = 'ReadSN data error ' + data
                    return False,data
        except Exception,e:
            self.message = "readsn exception " + e.message
            print "==========readsn excption=======%s\n"%str(e)
            return False,str(e)
        finally:
            self.lock.release()

    """
    @param timeout wait for time
    @return tuple(bool, str)
            0:success True,failed False
            1:success: like "0xfffe",failed,it is source dataor error message
            source data: like "ReadDI\n\nNAK\n>"
    """
    def readDI(self, timeout=1):
        try:
            self.lock.acquire()
            self.message = ''
            if self.main.isOpen() is False:
                self.__open()

            if self.main.isOpen():
                self.main.flushInput()
                command = "ReadDI\r"
                n = self.main.write(command)
                self.main.flushOutput()
                data = self.main.read(1)
                starttime = time.time()
                while True:
                    time.sleep(0.01)
                    n = self.main.inWaiting()
                    if(n == 0):
                        break
                    data = data+self.main.read(n)
                    if time.time()-starttime > timeout:
                        break

                lst = data.split("\r\n")
                if((len(lst)==5 or len(lst)==4) and (lst[3]=="OK" or lst[2]=="OK")):
                    return True, lst[2] if lst[2]<>"OK" else lst[1]
                else:
                    self.message = 'readDI data error ' + data
                    return False, data
            else:
                return False, "not open"
        except Exception, e:
            self.message = "readDI exception " + e.message
            return False, str(e)
        finally:
            self.lock.release()

    """
    @param timeout wait for time
    @return tuple(bool, str)
            0:success True,failed False
            1:success: like "0xfffe",failed,it is source data or error message
            source data: like "ReadDO\n\nNAK\n>" "ReadDO\n\n0xfffe\n>"
    """
    def readDO(self, timeout=1):
        try:
            self.lock.acquire()
            self.message = ''
            if self.main.isOpen() is False:
                self.__open()

            if self.main.isOpen() :
                self.main.flushInput()
                command="ReadDO\r"
                n=self.main.write(command)
                self.main.flushOutput()
                data = self.main.read(1)
                starttime = time.time()
                while True:
                    time.sleep(0.01)
                    n=self.main.inWaiting()
                    if(n==0):
                        break
                    if time.time()-starttime>timeout:
                        break
                    data=data+self.main.read(n)
                # print data
                lst = data.split("\r\n")
                if((len(lst)==5 or len(lst)==4) and (lst[3]=="OK" or lst[2]=="OK")):
                    return True,lst[2] if lst[2]<>"OK" else lst[1]
                else:
                    self.message = 'readDO data error ' + data
                    return False,data
        except Exception,e:
            self.message = "readDO exception " + e.message
            raise False,str(e)
        finally:
            self.lock.release()

    """
    @param index for IO Mapping.the value is 1~16
    @param timeout wait for time
    @return tuple(bool, str)
            0:success True,failed False
            1:success: like "0xfffe",failed,it is source data or error message
            source data: like "ReadDO\n\nNAK\n>" or "ReadDO\n\n0xfffe\n>"
    """
    def writeDO(self, index, status, timeout=10):
        try:
            self.lock.acquire()
            self.message = ''
            if self.main.isOpen() is False:
                self.__open()

            if self.main.isOpen():
                self.main.flushInput()
                command = "WriteDO %#.2x %#.2x\r"%(index,status)
                self.main.write(command)
                data = self.main.read(1000)
                starttime = time.time()
                while True:
                    n=self.main.inWaiting()
                    if(n==0):
                        break 
                    if time.time()-starttime>timeout:
                        break
                    data=data+self.main.read(n)
                # print data
                lst = data.split("\r\n")
                if lst[2]=="OK" or lst[1]=="OK":
                    return True,data
                else:
                    self.message = 'writeDO data error ' + data
                    return False,data
        except Exception,e:
            self.message = "writeDO exception " + e.message
            return False, "Exception:%s"%(str(e))
        finally:
            self.lock.release()


if __name__ == '__main__':
    innorev = InnorevController("COM8")
    print innorev.checkConnect()
    print innorev.readDO()
    print innorev.readDI()
    print innorev.ReadSN(10)
    print innorev.ReadID()
    # print innorev.WriteSN(2)
    print innorev.writeDO(2, 0)
    print innorev.readSingle(1, inputType=1)
    print innorev.readDI()
