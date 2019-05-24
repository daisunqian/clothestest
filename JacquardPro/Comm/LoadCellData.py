#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 2017-05-26

@author: Carl.liao
'''
import serial
import time
import logging
from PyQt4.QtCore import *
from queue import Queue


class LocalCell(object):
    
    def __init__(self):
        self.last_str = ""
        self.master = None

    # 自定连接
    def auto_connect(self, port_list):
        if port_list is None or len(port_list) == 0:
            return False, 'do not ports'
        try:
            for port in port_list:
                if self.master is not None:
                    self.master.close()
                try:
                    if self.OpenSerial(port)[0]:
                        time.sleep(0.2)
                        rtn = self.ReadLocalCellSigle()
                        if rtn != -1:
                            rtn_f = float(rtn)
                            return True, port
                except Exception, ex:
                    if self.master is not None:
                        self.master.close()
            return False, 'moon port connect fail'
        finally:
            if self.master is not None:
                self.master.close()

    def OpenSerial(self, port, braudate=19200):
        '''
        braudate is default set 19200 for loadcell hardware.
        '''
        try:
            self.master = serial.Serial(port, braudate)
            return (True, 'OK')
        except Exception, ex:
            return False, ex.message
        
    def CloseSerial(self):
        self.last_str = ""
        if self.master is not None:
            self.master.close()

    def ClearBuffer(self):
        #  discard all the data in cache
        #  begin to get loadcell data for
        if self.master.is_open is False:
            self.master.open()
        self.last_str = ""
        self.master.read_all()

    # 返回loadcell缓存全部有效数据
    def ReadLocalCell(self):
        '''
        Get all data from serial cache and ingore the first data when it is not a float.
        '''

        if self.master.is_open is False:
            self.master.open()

        str1 = self.master.read_all()
        if(len(str1) != 0):
            str1 = self.last_str + str1
            str_list = filter(None, str1.split(' '))
            self.last_str = str_list[len(str_list) - 1]
            return str_list[0:-1]
        else:
            return []

    # 返回最后一个有效数据
    def ReadLocalCellSigle(self, timeout=10):
        '''
        Get all data from serial cache and ingore the first data when it is not a float.
        '''

        if self.master.is_open is False:
            self.master.open()

        st = time.time()
        str1 = ''
        while time.time() - st <= timeout:
            str1 += self.master.read_all()
            # print str1
            # print '-'.center(100, '-')
            if(len(str1) != 0):
                str_list = filter(None, str1.split(' '))
                try:
                    # if len(str_list) > 0 and str_list[-1].index('.') >=1:         # 完整一个数据具有一个小数点
                    if len(str_list) > 0:  # 完整一个数据具有一个小数点
                        if len(str_list[-1]) >= 4:
                            f_data = float(str_list[-1])             # 最后一个数据为正常数据
                            return str_list[-1]
                        else:
                            if len(str_list) > 1:
                                f_data = float(str_list[-2])  # 最后一个数据为正常数据
                                return str_list[-2]
                    else:
                        continue
                except Exception, ex:
                    pass
        str1 += self.master.read_all()
        #  超时处理下数据
        if len(str1) > 0:
            str_list = filter(None, str1.split(' '))
            if len(str_list) > 1:
                return str_list[-2]
            else:
                return str_list[0] if len(str_list) > 0 else 'None'
        else:
            return 'None'

    # 测试使用，直接返回采集到的数据
    def read_test(self):
        str1 = self.master.read_all()
        if(len(str1) != 0):
            str1 = self.last_str + str1
            return str1
        else:
            return ''


if __name__ == '__main__':
    import time
    right = LocalCell()
    right.OpenSerial('COM5')
    right.ClearBuffer()
    while(True):
        print right.ReadLocalCellSigle(), '1111111'
        # print right.ReadLocalCell()
        time.sleep(0.02)