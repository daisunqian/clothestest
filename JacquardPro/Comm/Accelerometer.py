# -*- coding=utf-8 -*-

from serial import *
from PyQt4.QtCore import *
from queue import Queue
import Comm


# 加速器数据信息
class AccelerometerDataInfo(object):
    def __init__(self):
        self.xyz_acc = [0]*3               # x,y,z加速度
        self.xyz_angle_acc = [0]*3         # x,y,x角速度
        self.xyx_angle = [0]*3             # x,y,z角度
        self.temperature = 0               # 温度
        self.message = ''                  # 执行信息

    # 采集数据转换成对象数据
    def toAccelerometerDataInfo(self, databuff):
        # 85, 81, 36, 1, 10, 252, 153, 8, 115, 243, 216,
        # 85, 82, 0, 0, 0, 0, 0, 0, 115, 243, 13,
        # 85, 83, 88, 238, 31, 251, 124, 31, 115, 243, 9
        data_package = databuff
        print len(databuff)
        # print data_package
        while data_package is not None and len(data_package) > 0:
            if len(data_package) >= 11:
                datas = [0] * 4
                datas[0] = self.__to_short_int(data_package[3], data_package[2])
                datas[1] = self.__to_short_int(data_package[5], data_package[4])
                datas[2] = self.__to_short_int(data_package[7], data_package[6])
                datas[3] = self.__to_short_int(data_package[9], data_package[8])
                # print datas
                if data_package[1] == 0x51:
                    self.temperature = datas[3] / 100.0         # 第4个数据是温度
                    self.xyz_acc[0] = round(datas[0] / 32768.0 * 16, 3)
                    self.xyz_acc[1] = round(datas[1] / 32768.0 * 16, 3)
                    self.xyz_acc[2] = round(datas[2] / 32768.0 * 16, 3)
                elif data_package[1] == 0x52:
                    self.temperature = datas[3] / 100.0  # 第4个数据是温度
                    self.xyz_angle_acc[0] = round(datas[0] / 32768.0 * 2000, 3)
                    self.xyz_angle_acc[1] = round(datas[1] / 32768.0 * 2000, 3)
                    self.xyz_angle_acc[2] = round(datas[2] / 32768.0 * 2000, 3)
                    if self.xyz_angle_acc[0] == 0 and self.xyz_angle_acc[1] == 0 and self.xyz_angle_acc[2] == 0:
                        print 'xyz_angle_acc=0'
                elif data_package[1] == 0x53:
                    self.temperature = datas[3] / 100.0       # 第4个数据是温度
                    self.xyx_angle[0] = round(datas[0] / 32768.0 * 180, 3)
                    self.xyx_angle[1] = round(datas[1] / 32768.0 * 180, 3)
                    self.xyx_angle[2] = round(datas[2] / 32768.0 * 180, 3)
                else:
                    self.message = 'nosuppert type={0}, can not parse data'.format(hex(data_package[1]))

                if len(data_package) - 11 > 0:
                    data_package = data_package[11:]     # 下一包
                else:
                    data_package = []

        # if Comm.DEBUG:
        #     print '温度', self.temperature
        #     print '加速度', self.xyz_acc[0], self.xyz_acc[1], self.xyz_acc[2]
        #     print '角速度', self.xyz_angle_acc[0], self.xyz_angle_acc[1], self.xyz_angle_acc[2]
        #     print '角度', self.xyx_angle[0], self.xyx_angle[1], self.xyx_angle[2]

    # 高低字节转换成2字节有符号数据
    def __to_short_int(self, data_h, data_l):
        data = data_h << 8 | data_l
        # 最高位表示符号 if data_h >= 0xf0:
        if data_h & 0x80 == 0x80:  #
            data = data - 0xffff - 1
        return data

    # 字符串形式
    def tostring(self):
        return "{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(self.xyz_acc[0], self.xyz_acc[1], self.xyz_acc[2],
                                                            self.xyz_angle_acc[0], self.xyz_angle_acc[1], self.xyz_angle_acc[2],
                                                            self.xyx_angle[0], self.xyx_angle[1], self.xyx_angle[2])
        # str_values = '{' + '[' + str(self.xyz_acc[0]) + ' ' + str(self.xyz_acc[2]) + ' ' + str(self.xyz_acc[2]) + ']'
        # str_values += '-[' + str(self.xyz_angle_acc[0]) + ' ' + str(self.xyz_angle_acc[2]) + ' ' + str(self.xyz_angle_acc[2]) + ']'
        # str_values += '-[' + str(self.xyx_angle[0]) + ' ' + str(self.xyx_angle[2]) + ' ' + str(self.xyx_angle[2]) + ']' + '}'
        # return str_values
        # return str(self.xyz_acc) + '-' + str(self.xyz_angle_acc) + '-' + str(self.xyx_angle)

    # 获取加速度字符串形式
    def get_xyz_acc(self):
        return "{0},{1},{2}".format(self.xyz_acc[0], self.xyz_acc[1], self.xyz_acc[2])

    # 获取角速度字符串形式
    def get_xyz_angle_acc(self):
        return "{0},{1},{2}".format(self.xyz_angle_acc[0], self.xyz_angle_acc[1], self.xyz_angle_acc[2])

    # 获取角度字符串形式
    def xyx_angle(self):
        return "{0},{1},{2}".format(self.xyx_angle[0], self.xyx_angle[1], self.xyx_angle[2])


# 加速器数据采集以解析
class AccelerometerBll(QThread):

    def __init__(self, port, baudrate=115200):
        super(AccelerometerBll, self).__init__()
        self._port = port
        self._baudrate = baudrate
        self.master = None        # Serial(port, baudrate, 8, PARITY_NONE, STOPBITS_ONE)
        self.data_list = []       # 存储采集数据,每个数据是AccelerometerDataInf对象
        self._reading = False
        self.msg = ''

    # 自动查找端口
    # port_list端口集合
    def auto_connect(self, port_list):
        if port_list is None or len(port_list) == 0:
            return False, 'do not ports'
        for port in port_list:
            if self._port_check(port):
                self._port = port
                return True, port
            else:
                self.master = None

        return False, 'acc port connect fail'

    # 打开串口
    def open_serial(self):
        try:
            if self.master is None:
                self.master = Serial(self._port, self._baudrate, 8, PARITY_NONE, STOPBITS_ONE)
            if self.master.is_open is False:
                self.master.open()
            return True
        except Exception, ex:
            self.msg = ex.message
            return False

    # 关闭端口
    def close_serial(self):
        if self.master is not None:
            self.master.close()

    # 用于端口查找
    def _port_check(self, port, timeout=2):
        try:
            self._port = port
            if self.open_serial():
                starttime = time.time()
                respone_ls = []
                while time.time() - starttime <= timeout:
                    # try:
                    #     buf = self.master.read_all()
                    # except Exception, ex:
                    #     self.master = None
                    #     time.sleep(1)
                    #     self.open_serial()
                    buf = self.master.read_all()
                    if len(buf) > 0:
                        datals = [ord(data) for data in buf]
                        respone_ls.extend(datals)
                        while len(respone_ls) >= 11:
                            start_index = respone_ls.index(0x55)  # 找到起始0x55数据
                            if start_index >= 0:
                                respone_ls = respone_ls[start_index:]  # 移除非法数据
                                data_sum = sum(respone_ls[0:10])
                                if data_sum & 0xff == respone_ls[10]:
                                    if respone_ls[1] == 0x51 or respone_ls[1] == 0x52 or respone_ls[1] == 0x53:
                                        return True
                            else:
                                # 未找到起始，说明是非法数据，清除
                                respone_ls = []
                                time.sleep(0.02)
                    else:
                        time.sleep(0.02)
            return False
        except Exception, ex:
            return False
        finally:
            self.close_serial()

    # 清除串口缓存数据
    def clearBuff(self):
        try:
            if self.open_serial():
                self.master.read_all()
        except Exception, ex:
            self.master = None
            time.sleep(1)    # 等1秒后返回

    # 异步读数据，通过stop_read控制结束
    def read_data_async(self):
        self._reading = True
        self.start()

    # 返回加速器数据
    # clear=True每次读取先清除缓存数据
    # 返回None，表示未读到数据
    def read_data(self, clear=False, timeout=10):
        self._reading = True
        respone_ls = []
        # read_all = [False] * 3
        data_package = []
        self.open_serial()
        if clear:
            self.clearBuff()
        starttime = time.time()
        while time.time() - starttime <= timeout:
            buf = self.master.read_all()
            if len(buf) > 0:
                datals = [ord(data) for data in buf]
                respone_ls.extend(datals)
                while len(respone_ls) >= 11:
                    start_index = respone_ls.index(0x55)       # 找到起始0x55数据
                    if start_index >= 0:
                        respone_ls = respone_ls[start_index:]  # 移除非法数据
                        if len(respone_ls) < 11:               # 有效数据不足一个包
                            break
                        data_sum = sum(respone_ls[0:10])
                        if data_sum & 0xff == respone_ls[10]:
                            if respone_ls[1] == 0x51:
                                # read_all[0] = True
                                data_package = []  # 保证数据都是从0x51开始
                                data_package.extend(respone_ls[0:11])
                            if respone_ls[1] == 0x52:
                                # read_all[1] = True
                                data_package.extend(respone_ls[0:11])
                            if respone_ls[1] == 0x53:
                                # read_all[2] = True
                                data_package.extend(respone_ls[0:11])

                            respone_ls = respone_ls[11:]  # 下一包数据

                            # 三种数据采集完成
                            if len(data_package) == 33:                 # 三个包数据33字节
                                # read_all = [False] * 3           # 复位
                                acc_info = AccelerometerDataInfo()
                                acc_info.toAccelerometerDataInfo(data_package)
                                self.data_list.append(acc_info)
                                self.stop_read()
                                return acc_info
                        else:
                            respone_ls = respone_ls[1:]  # 校验码非法，从下一位开始查找
                            # print u' 校验位失败,下一个数据开始'
                    else:
                        # 未找到起始，说明是非法数据，清除
                        respone_ls = []
                        time.sleep(0.01)
        self.stop_read()
        return None

    # 读角速度
    def read_angle_acc(self, timeout=2):
        self._reading = True
        self.data_list = []
        respone_ls = []
        collect_ls = []
        # read_all = [False] * 3
        data_package = []
        self.open_serial()
        starttime = time.time()
        buf = ''
        while time.time() - starttime <= timeout:
            buf += self.master.read_all()
        if len(buf) > 0:
            datals = [ord(data) for data in buf]
            respone_ls.extend(datals)
            while len(respone_ls) >= 11:
                start_index = respone_ls.index(0x55)  # 找到起始0x55数据
                if start_index >= 0:
                    respone_ls = respone_ls[start_index:]  # 移除非法数据
                    if len(respone_ls) < 11:  # 有效数据不足一个包
                        break
                    data_sum = sum(respone_ls[0:10])
                    if data_sum & 0xff == respone_ls[10]:
                        if respone_ls[1] == 0x52:
                            data_package.extend(respone_ls[0:11])

                        respone_ls = respone_ls[11:]  # 下一包数据

                        # 三种数据采集完成
                        if len(data_package) == 11:  # 1个包数据11字节
                            acc_info = AccelerometerDataInfo()
                            acc_info.toAccelerometerDataInfo(data_package)
                            self.data_list.append(acc_info)
                            collect_ls.append(acc_info.xyz_angle_acc)
                            data_package = []
                    else:
                        respone_ls = respone_ls[1:]  # 校验码非法，从下一位开始查找
                        # print u' 校验位失败,下一个数据开始'
                else:
                    # 未找到起始，说明是非法数据，清除
                    respone_ls = []
                    time.sleep(0.01)
        self.stop_read()
        return collect_ls

    # 后台采集并解析数据，存储到self.data_list列表,每个数据是AccelerometerDataInfo对象
    def run(self):
        respone_ls = []
        read_all = [False]*3
        data_package = []
        self.open_serial()
        while self._reading:
            buf = self.master.read_all()
            if len(buf) > 0:
                datals = [ord(data) for data in buf]
                respone_ls.extend(datals)
                while len(respone_ls) >= 11:
                    if self._reading is False:
                        break
                    start_index = respone_ls.index(0x55)  # 找到起始0x55数据
                    if start_index >= 0:
                        respone_ls = respone_ls[start_index:]  # 移除非法数据
                        if len(respone_ls) < 11:  # 有效数据不足一个包
                            # print respone_ls, 'respone_ls'
                            break
                        data_sum = sum(respone_ls[0:10])
                        if data_sum & 0xff == respone_ls[10]:
                            if respone_ls[1] == 0x51:
                                # read_all = [False] * 3            # 复位
                                # read_all[0] = True
                                data_package = []                 # 保证数据都是从0x51开始
                                data_package.extend(respone_ls[0:11])
                            if respone_ls[1] == 0x52:
                                # read_all[1] = True
                                data_package.extend(respone_ls[0:11])
                            if respone_ls[1] == 0x53:
                                # read_all[2] = True
                                data_package.extend(respone_ls[0:11])

                            respone_ls = respone_ls[11:]  # 下一包数据

                            # 三种数据采集完成
                            # if read_all[0] and read_all[1] and read_all[2]:
                            if len(data_package) == 33:  # 三个包数据33字节
                                # print data_package, 'data_package'
                                # read_all = [False]*3
                                acc_info = AccelerometerDataInfo()
                                acc_info.toAccelerometerDataInfo(data_package)
                                self.data_list.append(acc_info)
                                data_package = []
                    else:
                        # 未找到起始，说明是非法数据，清除
                        respone_ls = []

    # 停止采集
    def stop_read(self):
        self._reading = False
        self.close_serial()


TEST_TYPE=2
if __name__ == '__main__':
    acc_bll = AccelerometerBll("COM10")
    print acc_bll.auto_connect(["COM10"])

    lsss = acc_bll.read_angle_acc(1)
    print lsss
    print len(lsss)
    # acc_bll.test()
    # acc_info = AccelerometerDataInfo()
    # databuff = [85, 83, 89, 243, 154, 253, 186, 166, 183, 247, 153]
    # acc_info.toAccelerometerDataInfo(databuff)

    # while True:
    #     acc_info = acc_bll.read_data()
    #     print '-'.center(100, '-')
    #     print 'temperature={0}'.format(acc_info.temperature)
    #     print 'accelerated speed ={0},{1},{2}'.format(acc_info.xyz_acc[0], acc_info.xyz_acc[1], acc_info.xyz_acc[2])
    #     print 'angular speed ={0},{1},{2}'.format(acc_info.xyz_angle_acc[0], acc_info.xyz_angle_acc[1],
    #                                                        acc_info.xyz_angle_acc[2])
    #     print 'angle = {0},{1},{2}'.format(acc_info.xyx_angle[0], acc_info.xyx_angle[1], acc_info.xyx_angle[2])
    #     print '-'.center(100, '-')
    #     time.sleep(1)

    print 'thread end'
        # acc_info = acc_bll.read_data()
        # print 'temperature={0}'.format(acc_info.temperature)
        # print 'accelerated speed ={0},{1},{2}'.format(acc_info.xyz_acc[0], acc_info.xyz_acc[1], acc_info.xyz_acc[2])
        # print 'angular speed ={0},{1},{2}'.format(acc_info.xyz_angle_acc[0], acc_info.xyz_angle_acc[1],
        #                                           acc_info.xyz_angle_acc[2])
        # print 'angle = {0},{1},{2}'.format(acc_info.xyx_angle[0], acc_info.xyx_angle[1], acc_info.xyx_angle[2])
        # print '-'.center(100, '-')
        # for data in acc_bll.data_list:
        #     print '加速度' , data.xyz_acc[0],data.xyz_acc[1],data.xyz_acc[2]
        #     print '角速度', data.xyz_angle_acc[0], data.xyz_angle_acc[1], data.xyz_angle_acc[2]
        #     print '角度', data.xyx_angle[0], data.xyx_angle[1], data.xyx_angle[2]