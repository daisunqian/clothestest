# -*- coding=utf-8 -*-

from serial import *
import math
# from PyQt4.QtCore import *
# from queue import Queue
import pandas


# mcu 数据采集
class MCUComm(object):

    def __init__(self, port, baudrate=115200, bytesize=EIGHTBITS, parity=PARITY_NONE,stopbits=STOPBITS_ONE):
        self.req_cmd = ''     # 请求数据
        self.res_cmd = ''     # 响应数据
        self.message = ''     # 执行信息
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.mcu_main = None   # Serial(port, baudrate, bytesize, parity, stopbits)
        self.timeout = 2

    # 自动查找端口
    # port_list端口集合
    def auto_connect(self, port_list):
        if port_list is None or len(port_list) == 0:
            return False, 'do not ports'
        for port in port_list:
            if self.mcu_main is not None:
                self.mcu_main.close()
            try:
                self.mcu_main = Serial(port, self.baudrate, self.bytesize, self.parity, self.stopbits, self.timeout)

                if self.checkConnect():
                    self.port = port
                    return True, port
                else:
                    self.mcu_main.close()
                    self.mcu_main = None
            except Exception, ex:
                if self.mcu_main is not None:
                    self.mcu_main.close()
            finally:
                if self.mcu_main is not None:
                    self.mcu_main.close()

        return False, 'io port connect fail'

    # 检查端口
    def checkConnect(self):
        try:
            if self.OpenPort():
                self.mcu_main.write('\r')
                time.sleep(0.01)
                self.mcu_main.write("F")
                time.sleep(0.01)
                data = self.mcu_main.read_all()
                if len(data) > 0 and data.lower().find("this is mcu port") >= 0:
                    return True
                else:
                    return False
        except Exception, ex:
            self.message = "check connect exception:" + ex.message
            return False

    # 端口打开
    def OpenPort(self):
        try:
            self.message = ''
            if self.mcu_main is None:
                self.mcu_main = Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits)
            if self.mcu_main.is_open is False:
                self.mcu_main.open()
            return self.mcu_main.is_open
        except Exception, ex:
            self.mcu_main = None
            self.message = 'port open fail: {0}'.format(ex.message)
            return False

    # 端口关闭
    def ClosePort(self):
        self.message = 'close port'
        if self.mcu_main is not None and self.mcu_main.is_open:
            self.mcu_main.read_all()     # 清除缓存数据
            self.message = '{0} port close'.format(self.mcu_main.port)
            self.mcu_main.close()

    # 直接跟dut连接时，需调用该函数更改模式
    # 延时是客户要求
    def init(self):
        try:
            if self.OpenPort():
                # 模式设置
                self.mcu_main.write([0x03])
                time.sleep(0.1)
                # start
                self.mcu_main.write([0x20, 0x08, 0x04])
                time.sleep(0.1)
                # uart mode
                self.mcu_main.write([0x02])
                time.sleep(0.1)
                return True
            else:
                return False
        except Exception, ex:
            self.message = 'send init command exception :' + ex.message
            return False

    # 发送命令通知mcu开始测试
    def mcu_start(self):
        try:
            if self.OpenPort():
                self.mcu_main.write("\r")
                time.sleep(0.01)
                # self.mcu_main.write("K")
                # time.sleep(0.5)
                return True
        except Exception, ex:
            self.message = "mcu_start exception:" + ex.message
            return False

    # 读 i 命令
    def Read_I(self):
        try:
            if self.OpenPort():
                self.mcu_main.write("i")
                data = self.mcu_main.read_all()
                starttime = time.time()
                while time.time()-starttime <= self.timeout:
                    data = data + self.mcu_main.read_all()
                    if len(data.split('\r\n')) >= 23:   # 返回数据应该在22行+ 1个空行
                        break
                # 检测退出后在执行一次采集,避免数据未接收完
                data = data + self.mcu_main.read_all()

                if len(data) == 0:
                    self.message = 'i command not response'
                return data
        except Exception, ex:
            self.message = 'send i command exception :' + ex.message
            return ''
        finally:
            self.ClosePort()

    # 发送 r 命令,发送后数据持续上传到缓存中
    # 在Prox和TOUCH0-11上连续报告电容，直到按下<Enter>键
    def Send_R(self):
        try:
            if self.OpenPort():
                self.mcu_main.write("r")
                return True
        except Exception, ex:
            self.message = 'send i command exception :' + ex.message
            return False

    # 开始发送t命令
    # 返回计算参数数据，dut 等待接收任意数据，继续传输diff数据
    def Start_T(self, timeout=10):
        try:
            if timeout <= 0:
                timeout = 10

            if self.OpenPort():
                self.mcu_main.write('*')  # 发送任意数据，停止dut数据上传
                self.ClosePort()
                time.sleep(0.02)

            if self.OpenPort():
                self.mcu_main.read_all()
                self.mcu_main.write("t")
                st = time.time()
                data = ''
                msg = 'start t fail'
                status = False
                while time.time() - st <= timeout:
                    data += self.mcu_main.read_all()
                    if len(data.split('\r\n')) >= 15:              # 发送t命令返回14行数据
                        time.sleep(0.01)
                        data += self.mcu_main.read_all()
                        status = True
                        msg = 'ok'
                        break
                print data
                return status, data if status else msg
        except Exception, ex:
            self.message = 'send i command exception :' + ex.message
            return False, self.message

    # 该操作前需调用Start_T操作开启
    # 读 t 命令,发送后数据持续上传到缓存中
    # 持续报告相邻两条上的电容差值和TOUCH0-11直到<Enter>键被按下
    # 返回数据：(状态， msg）
    def Start_T_Collect(self):
        try:
            if self.OpenPort():
                # 发送任意数据，开始采集数据
                self.mcu_main.write("1")
                return True, 'ok'
        except Exception, ex:
            self.message = 'send i command exception :' + ex.message
            return False, self.message

    # 停止t命令数据上报
    def Stop_T(self):
        try:
            if self.OpenPort():
                # 发送<Enter>键结束
                self.mcu_main.write([0x0D])
                time.sleep(0.5)
                return True
        except Exception, ex:
            self.message = 'send i command exception :' + ex.message
            return False
        finally:
            self.ClosePort()

    # 读端口数据
    def Read_Buff(self):
        try:
            if self.OpenPort():
                return self.mcu_main.read_all()
            else:
                return ""
        except Exception, ex:
            self.message = 'read data exception :' + ex.message
            return ""

    # 使能振动器
    def Enable_Haptics(self):
        try:
            if self.OpenPort():
                self.mcu_main.write('*')
                time.sleep(0.01)
                self.mcu_main.write('V')
                time.sleep(0.05)
                # 有响应数据吗？
                return True
        except Exception, ex:
            self.message = 'send V command exception :' + ex.message

    # 振动器去使能
    def Disable_Haptics(self):
        try:
            if self.OpenPort():
                self.mcu_main.write('v')
                # 有响应数据吗？是 'Haptics disabled'吗？
                return True
        except Exception, ex:
            self.message = 'send v command exception :' + ex.message
            return False
        finally:
            self.ClosePort()

    # led 控制命令
    # r,g,b是RGB 颜色值
    def led_control(self, r="FF", g="FF", b="FF"):
        try:
            if self.OpenPort():
                self.mcu_main.write('l')
                time.sleep(0.05)
                self.mcu_main.write("{0}{1}{2}".format(r, g, b))
                time.sleep(0.05)
                # 有响应数据吗?
                return True
        except Exception, ex:
            self.message = 'send l command exception :' + ex.message
            return False
        finally:
            self.ClosePort()

    # 关闭上报,同时关闭mcu通讯模式
    def close_up(self):
        try:
            if self.OpenPort():
                self.mcu_main.write('\r')
                self.mcu_main.read_all()
                return True
        except Exception, ex:
            self.message = 'send close_up command exception :' + ex.message
            return False
        finally:
            self.ClosePort()


# 命令返回的用于计算的数据集
class CalculateParameter(object):
    HFCLK_Frequency = 48000

    def __init__(self):
        self.VREF = 2.021
        self.CSD_tuning_mode = 1
        self.Scan_Resolution = 12
        self.Sense_Clock_Frequency = 8
        self.Modulation_Clock_Frequency = 1
        self.Noise_Threshold = 57  # 噪声阈值
        self.Modulation_IDAC_Value = 14
        self.Compensation_IDAC_Values = ''
        self.prox = 0
        self.L0_L11 = [0] * 12
        self.records = []  # 采集的raw count 数据
        self.roll_records = []    # 滚动采集raw count数据


# 衣服，背包命令i返回数据信息
# i命令数据
class InterposerInfo(CalculateParameter):

    def __init__(self):
        super(InterposerInfo, self).__init__()
        self.command_datas = ''
        self.ZCommand = ''
        self.Mfg_firmware_version = ''
        self.Mfg_build_date = ''
        self.Manufacturing_ID = ''         # SN
        self.Google_ID = ''
        self.Gear_ID = ''
        self.Vendor_ID = ''
        self.Product_ID = ''
        self.Hardware_revision = ''
        InterposerInfo.HFCLK_Frequency = 48000              # HFCLK Frequency 公式中需使用
        self.Cap_sense_config = ''
        self.VREF = 2.021
        self.CSD_tuning_mode = ''
        self.Scan_Resolution = 13              # Scan Resolution 公式中需使用(N值获取)
        self.Sense_Clock_Frequency = 8                  # Sense Clock Frequency Divider,公式中需使用
        self.Modulation_Clock_Frequency = 1              # Modulation Clock Frequency Divider,公式中需使用
        self.Modulation_IDAC_Value = 14        # Modulation IDAC Value,公式中需使用
        self.Noise_Threshold = 37
        self.Compensation_IDAC_Values = ''     # Compensation IDAC Values,公式中需使用
        self.prox = ''            # prox数据
        self.L0_L11 = []          # L0,L1,L2,..L11数据

    # 采集数据转换
    def toInterposerInfo(self, data):
        try:
            if data is not None and len(data) > 0:
                self.command_datas = data
                datas = data.split('\r\n')
                # 找到command命令的起始
                index = -1
                for i, tempdata in enumerate(datas):
                    # if data.lower().find("command") >= 0:
                    if tempdata.lower().find("command: info") >= 0:
                        index = i
                        break
                if index >= 0:
                    datas = datas[index:]
                    self.ZCommand = datas[0].split(':')[1]
                    self.Mfg_firmware_version = datas[1].split(':')[1]
                    self.Mfg_build_date = datas[2].split(':')[1]
                    # Factory config:
                    self.Manufacturing_ID = datas[4].split(':')[1]
                    self.Google_ID = datas[5].split(':')[1]
                    self.Gear_ID = datas[6].split(':')[1]
                    self.Vendor_ID = datas[7].split(':')[1]
                    self.Product_ID = datas[8].split(':')[1]
                    self.Hardware_revision = datas[9].split(':')[1]
                    # HFCLK Frequency 公式中需使用48000kHz
                    hfclk = datas[10].split(':')[1].lower().replace("khz", "")
                    InterposerInfo.HFCLK_Frequency = int(hfclk)
                    # Cap-sense config:
                    self.Cap_sense_config = datas[11].split(':')[1]
                    self.VREF = int(datas[12].split(':')[1]) / 1000.000
                    self.CSD_tuning_mode = datas[13].split(':')[1]
                    # Scan Resolution 公式中需使用(N值获取)
                    self.Scan_Resolution = int(datas[14].split(',')[1].split('=')[1])
                    # Sense Clock Frequency Divider,公式中需使用
                    self.Sense_Clock_Frequency = int(datas[15].split(',')[1].split('=')[1])
                    # Modulation Clock Frequency Divider,公式中需使用
                    self.Modulation_Clock_Frequency = int(datas[16].split(':')[1])
                    self.Noise_Threshold = int(datas[17].split(',')[1].split('=')[1])
                    # Modulation IDAC Value,公式中需使用
                    self.Modulation_IDAC_Value = int(datas[18].split(',')[1].split('=')[1])
                    # Compensation IDAC Values,公式中需使用,即是 Prox,L0,L1,L2...L11数据
                    self.Compensation_IDAC_Values = datas[21]
                    values = self.Compensation_IDAC_Values.split(',')
                    self.prox = int(values[0])
                    self.L0_L11 = [int(data) for data in values[1:]]
                    return True, 'ok'
                else:
                    return False, 'toInterposerInfo Invalid Format'
            else:
                return False, 'convert data is null'
        except Exception, ex:
            return False,  "InterposerInfo-toInterposerInfo -exception" + ex.message


# t 命令返回的公式计算参数数据，返回的数据同i命令读出相关数据一样
class TcmdInfo(CalculateParameter):

    def __init__(self):
        super(TcmdInfo, self).__init__()
        self.collect_cmd_info = ''          # 采集到数据
        self.ZCommand = 'info'
        # self.VREF = 2.021
        # self.CSD_tuning_mode = 1
        # self.Scan_Resolution = 12
        # self.Sense_Clock_Frequency = 8
        # self.Modulation_Clock_Frequency = 1
        # self.Noise_Threshold = 57                     # 噪声阈值
        # self.Modulation_IDAC_Values = 14
        # self.Compensation_IDAC_Values = ''
        # self.prox = 0
        # self.L0_L11 = [0]*12
        # self.records = []  # 采集的diff数据

    def toTcmdInfo(self, data):
        try:
            self.collect_cmd_info = data
            if data is not None and len(data) > 0:
                datas = data.split('\r\n')
                # 找到command命令的起始
                index = -1
                for i, data in enumerate(datas):
                    if data.lower().find("command") >= 0:
                        index = i
                        break
                if index >= 0:
                    datas = datas[index:]
                    self.ZCommand = datas[0].split(':')[1]
                    # Cap-sense config:
                    self.VREF = int(datas[2].split(':')[1]) / 1000.000
                    self.CSD_tuning_mode = datas[3].split(':')[1]
                    self.Scan_Resolution = int(datas[4].split(',')[1].split('=')[1])
                    self.Sense_Clock_Frequency = int(datas[5].split(',')[1].split('=')[1])
                    self.Modulation_Clock_Frequency = int(datas[6].split(':')[1])
                    self.Noise_Threshold = datas[7].split(',')[1].split('=')[1]  # 噪声阈值
                    self.Modulation_IDAC_Value = int(datas[8].split(',')[1].split('=')[1])
                    self.Compensation_IDAC_Values = datas[11]
                    values = self.Compensation_IDAC_Values.split(',')
                    self.prox = int(values[0])
                    self.L0_L11 = [int(data) for data in values[1:]]
                    return True, 'ok'
                else:
                    return False, 'toTcmdInfo Invalid Format'
            else:
                return False, 'convert data is nll'
        except Exception, ex:
            return False, "TcmdInfo-toTcmdInfo -exception" + ex.message

    # 采集数据转换
    def to_touch_diff(self, records):
        try:
            if records is not None and len(records) > 0:
                self.records = []
                datas = records.split('\r\n')
                # 检测起始位置
                index = -1
                record_list = []
                for i, data in enumerate(datas):
                    if data.lower().find('Press any key to stop'.lower()) >= 0:
                        index = i
                        record_list = datas[i+2:]
                        break
                    elif data.lower().find("Prox L0  L1  L2  L3  L4  L5  L6  L7  L8  L9  L10 L11".lower()) >= 0:
                        index = i
                        record_list = datas[i+1:]
                        break
                # 重新赋值
                if index >= 0:
                    datas = datas[index:]
                else:
                    record_list = datas

                # # 检测是不是 "检测第1行是不是 Press any key to stop"
                # if datas[0].lower().find('Press any key to stop'.lower()) >= 0:
                #     record_list = datas[2:]
                # elif datas[0].lower().find("Prox L0  L1  L2  L3  L4  L5  L6  L7  L8  L9  L10 L11".lower()) >= 0:
                #     record_list = datas[1:]
                # else:
                #     record_list = datas

                for record in record_list:
                    try:
                        ls = [int(data) for data in record.split(',')[1:]]  # 第1个是prox数据，从第二个开始
                        if len(ls) == 12:
                            self.records.append(ls)
                    except Exception, ex:
                        pass
                return True, 'ok'
            else:
                return False, 'convert to data is no'
        except Exception, ex:
            return False, "TcmdInfo-to_touch_diff -exception" + ex.message


# r命令采集数据分析
class RcmdInfo(CalculateParameter):
    def __init__(self):
        super(RcmdInfo, self).__init__()
        self.command_datas = ''
        self.ZCommand = 'info'
        # self.VREF = 2021
        # self.CSD_tuning_mode = 1
        # self.Scan_Resolution = 12
        # self.Sense_Clock_Frequency = 8
        # self.Modulation_Clock_Frequency = 1
        # self.Noise_Threshold = 57  # 噪声阈值
        # self.Modulation_IDAC_Value = 14
        # self.Compensation_IDAC_Values = ''
        # self.prox = 0
        # self.L0_L11 = [0] * 12
        # self.records = []                  # 采集的raw count 数据

    def toIcmdInfo(self, data):
        try:
            self.command_datas = data
            if data is not None and len(data) > 0:
                self.records = []
                datas = data.split('\r\n')
                # 找到command命令的起始
                index = -1
                for i, data in enumerate(datas):
                    if data.lower().find("command") >= 0:
                        index = i
                        break
                if index >= 0:
                    datas = datas[index:]
                    self.ZCommand = datas[0].split(':')[1]
                    # Cap-sense config:
                    self.VREF = int(datas[2].split(':')[1]) / 1000.000
                    self.CSD_tuning_mode = datas[3].split(':')[1]
                    self.Scan_Resolution = int(datas[4].split(',')[1].split('=')[1])
                    self.Sense_Clock_Frequency = int(datas[5].split(',')[1].split('=')[1])
                    self.Modulation_Clock_Frequency = int(datas[6].split(':')[1])
                    self.Noise_Threshold = datas[7].split(',')[1].split('=')[1]  # 噪声阈值
                    self.Modulation_IDAC_Value = int(datas[8].split(',')[1].split('=')[1])
                    self.Compensation_IDAC_Values = datas[11]
                    values = self.Compensation_IDAC_Values.split(',')
                    self.prox = int(values[0])
                    self.L0_L11 = [int(data) for data in values[1:]]
                    record_list = datas[14:]  # 第15行开始数据是raw count
                    for record in record_list:
                        ls = [int(data) for data in record.split(',')[1:]]
                        if len(ls) == 12:
                            self.records.append(ls)  # 第1个是prox数据，从第二个开始

                    # print len(self.records)
                    return True, 'ok'
                else:
                    return False, 'toTcmdInfo Invalid Format'
            else:
                return False, 'convert data is null'
        except Exception, ex:
            return False, "RcmdInfo-toIcmdInfo -exception" + ex.message

    # raw count 数据转换成difference数据
    # 参数:data是滚动时采集的raw count 数据
    def todifferenceInfo(self, data):
        try:
            status = False
            self.command_datas = data
            if data is not None and len(data) > 0:
                self.roll_records = []
                datas = data.split('\r\n')
                for record in datas:
                    if len(record) > 1:
                        try:
                            ls = [int(data1) for data1 in record.split(',')[1:]]  # 第1个是prox数据，从第二个开始
                            if len(ls) == 12:
                                status = True
                                self.roll_records.append(ls)
                        except Exception, ex:
                            pass
                return status, 'ok'
            else:
                return False, 'convert data is null'
        except Exception, ex:
            return False, "RcmdInfo-todifferenceInfo -exception" + ex.message


# 产品执行业务逻辑处理
# 包含公式计算
class InterposerBll(object):
    Noise_raw_count = "Noise raw count"
    Baseline_raw_count = "baseline raw count"
    Effective_dynamic_range = "effective dynamic range"
    Baseline = "Baseline"
    Differenve_Max_data = "Differenve Max data"
    Differenve_Max_Cap = "max touch capacitance"
    Touch_saturation = "touch saturation"
    Centroid_pos = "centroid"
    Sensor_NO = "Sensor_NO"           # 根据Centroid_pos计算出的sensor 编号

    CS_KEYS = [Noise_raw_count, Baseline_raw_count, Effective_dynamic_range, Baseline]

    def __init__(self, port, baudrate=115200):
        self.mcu_com = MCUComm(port, baudrate)
        self.current_Info = InterposerInfo()              # 执行i命令读取数据信息对象
        self.t_cmdInfo = TcmdInfo()                       # t 命令返回的计算类型数据，同i命令相应数据一直
        self.r_cmdinfo = RcmdInfo()                       # r 命令返回的计算类型数据，同i命令相应数据一直
        # true表示在采集数据
        self.collecting = False
        # 计算raw count记录数据(Noise raw count, baseline raw count, effective dynamic range, Baseline)
        self.raw_count_datas = {InterposerBll.Noise_raw_count: [],
                                InterposerBll.Baseline_raw_count: [],
                                InterposerBll.Effective_dynamic_range: [],
                                InterposerBll.Baseline: []}
        # 对应raw_count_datas数据的电容值
        self.raw_count_Capacitance = {InterposerBll.Noise_raw_count: [],
                                      InterposerBll.Baseline_raw_count: [],
                                      InterposerBll.Effective_dynamic_range: [],
                                      InterposerBll.Baseline: []}

        # difference_data_processing计算出的每条sensor最大电容值,touch saturation，centroid数据(触摸位置),
        # 根据Centroid_pos计算出的sensor 编号->格式：{"L0":[]...."L11":[]}
        self.difference_cal_datas = {InterposerBll.Differenve_Max_data: [],
                                     InterposerBll.Differenve_Max_Cap: [],
                                     InterposerBll.Touch_saturation: [],
                                     InterposerBll.Centroid_pos: [],
                                     InterposerBll.Sensor_NO: []}

    # 采集raw count 数据
    # 参数：采集最少记录条数，默认是50条记录
    def read_raw_count(self, count=50, timeout=15):
        if timeout <= 0:
            timeout = 15
        try:
            if self.mcu_com.Send_R():
                count += 15                     # 前14行数据是cmd info数据
                raed_str = ''
                self.collecting = True
                st = time.time()
                while time.time() - st <= timeout:
                    raed_str += self.mcu_com.Read_Buff()
                    if len(raed_str.split('\r\n')) >= count+14:
                        raed_str += self.mcu_com.Read_Buff()
                        break
                self.collecting = False
                #  数据处理
                print raed_str
                self.r_cmdinfo.toIcmdInfo(raed_str)
                return True, 'ok'
            else:
                return False, self.mcu_com.message
        except Exception, ex:
            return False, ex.message
        finally:
            # self.mcu_com.close_up()
            pass

    # 采集raw count 数据
    def collect_raw_count(self):
        self.collecting = True
        raed_str = ''
        while self.collecting:
            st=self.mcu_com.Read_Buff()
            print st
            raed_str += st
        raed_str += self.mcu_com.Read_Buff()
        self.mcu_com.ClosePort()
        self.r_cmdinfo.todifferenceInfo(raed_str)
        print raed_str
        # 解析出返回用于计算的数据
        return len(raed_str) > 0

    # 打开t命令
    def start_t(self):
        status, data = self.mcu_com.Start_T()
        if status:
            status, data = self.t_cmdInfo.toTcmdInfo(data)
        return status, data

    # 需通过 start_t命令开启t命令
    # 接触dut时,采集数据
    # 返回：失败返回(False, msg),成功返回(True，采集数据)
    def read_touch_data(self):
        status, data = self.mcu_com.Start_T_Collect()
        if status:
            self.collecting = True
            raed_str = ''
            while self.collecting:
                raed_str += self.mcu_com.Read_Buff()
            # st = time.time()
            # while time.time() - st <= 5:
            #     raed_str += self.mcu_com.Read_Buff()
            self.mcu_com.ClosePort()
            print raed_str
            # 解析出返回用于计算的数据
            return self.t_cmdInfo.to_touch_diff(raed_str)
        else:
            return status, data

    # 停止采集
    def stop_collect(self):
        self.collecting = False
        self.mcu_com.close_up()

    # 获取产品配置信息
    def get_facetoy_config(self):
        cnt = 2
        status, msg = False, ''
        while cnt > 0:
            cnt -= 1
            info_list = self.mcu_com.Read_I()
            if info_list is None or len(info_list) == 0:
                self.mcu_com.init()
                status, msg = False, self.mcu_com.message
                continue
            else:
                # file_path = '.\i_command_info.txt'
                # # 将数据写入到文件中
                # with open(file_path, 'w') as fp:
                #     fp.write(str(info_list))

                status, msg = self.current_Info.toInterposerInfo(info_list)
                if status is False:
                    self.mcu_com.init()
                    continue
        return status, msg

    # 开始振动测试
    def start_Haptics(self):
        return self.mcu_com.Enable_Haptics()

    # 停止振动测试
    def stop_Haptics(self):
        return self.mcu_com.Disable_Haptics()

    # 开始led等测试
    # r,g,b是RGB 颜色值
    def start_led(self, r="FF", b="FF", g="FF"):
        return self.mcu_com.led_control(r, b, g)

    # 读出的sensor的Compensation IDAC
    def _I_comp(self, l_value):
        return l_value * 2.4*math.pow(10, -6)

    # 公式gc计算
    def GC(self, parameter):
        # 公式中fs计算
        # Sense Clock Frequency
        # Sense Clock Frequency = Modulation Clock Frequency/Sense Clock Frequency Divider
        # Modulation Clock Frequency = HFCLK/Modulation Clock Frequency Divider
        # HFCLK_Frequency单位：kHz
        modulation_c_f = parameter.HFCLK_Frequency * 1000.0 / parameter.Modulation_Clock_Frequency
        f_s = modulation_c_f/parameter.Sense_Clock_Frequency
        V_REF = parameter.VREF
        N = parameter.Scan_Resolution
        I_mod = parameter.Modulation_IDAC_Value * 2.4*math.pow(10, -6)
        return (math.pow(2, N) - 1) * V_REF*f_s/I_mod

    # 计算公式raw count
    # 参数：parameter命令返回的计算参数,,cs电容值, L_value感应线的Compensation IDAC数据
    def raw_count(self, parameter, cs, L_value):
        gc = self.GC(parameter)
        I_comp = L_value*2.4
        N = parameter.Scan_Resolution
        temp_pow = math.pow(2, N) - 1
        I_mod = parameter.Modulation_IDAC_Value * 2.4
        temp = I_comp/I_mod       # I_comp/I_mod

        return gc*cs - temp_pow * temp

    # 计算电容值
    # 输入参数：parameter命令返回的计算参数, rawcount, 即通过r命令读出的数据,L_value感应线的Compensation IDAC数据
    def CS_rawcount(self, parameter, rawcount, L_value):
        gc = self.GC(parameter)
        I_comp = L_value*2.4           # self._I_comp(L_value)
        I_mod = parameter.Modulation_IDAC_Value * 2.4
        temp = I_comp / I_mod
        N = parameter.Scan_Resolution
        temp_pow = math.pow(2, N) - 1
        return (rawcount + temp_pow*temp)/gc * pow(10, 12)

    # 计算电容值
    # 参数：parameter命令返回的计算参数,diff即两个seneor线之间的差值,即通过t命令读出的数据
    def CS_diff(self, parameter, diff):
        gc = self.GC(parameter)
        if gc == 0:
            return 0
        else:
            return diff/gc * math.pow(10, 12)

    # 计算接触位置
    # 参数：diffs->t命令采集differenc数据
    # 参数：indexs->sensor线index(0---11)
    def centroid(self, diffs, indexs=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]):
        temp1 = 0
        index = 0
        for i in indexs:
            temp1 += i*diffs[index]
            index += 1
        temp2 = sum(diffs)
        if temp2 == 0:
            return 0
        else:
            return temp1*1.0/temp2

    # 将采集的raw count 数据转换成cs数据(即：电容值)
    # 参数：rawcount 数据记录[[L0..L11], [L0...L11]]
    # 参数：l_values : L0---L11 的计算数据
    def to_CS(self, parameter, rowcount_datas, l_values):
        record_ls = []
        for rowcount in rowcount_datas:
            if len(rowcount) == 12:
                l_cs = []
                for value, data in zip(l_values, rowcount):
                    cs = self.CS_rawcount(parameter, data, value)
                    l_cs.append(cs)
                record_ls.append(l_cs)
        return record_ls

    # 将采集的sensor difference数据转换成电容值
    def to_CS_diff(self, parameter, diff_datas):
        record_ls = []
        for rowcount in diff_datas:
            ls = [self.CS_diff(parameter, da) for da in rowcount]
            if len(ls) > 0:
                record_ls.append(ls)

        return record_ls

    # 计算每列的Nois raw count, baseline raw count, effective dynamic range, ​Baseline
    def calculate(self, rawcounts):
        # 计算raw count记录数据(Noise raw count, baseline raw count, effective dynamic range, Baseline)
        self.raw_count_datas = {InterposerBll.Noise_raw_count: [], InterposerBll.Baseline_raw_count: [],
                                InterposerBll.Effective_dynamic_range: [], InterposerBll.Baseline: []}
        if rawcounts is not None and len(rawcounts) > 0:
            N = self.current_Info.Scan_Resolution
            max_raw_count = math.pow(2, N) - 1
            columns = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11"]
            df = pandas.DataFrame(rawcounts)
            df.columns =columns
            # self.noise_raw_count = []
            # self.baseline_raw_count = []
            # self.effective_dynamic_range = []
            # self.baseline = []            # ​Baseline %​ by = Baseline Raw Count/Max Raw Count
            for column in columns:
                self.raw_count_datas[InterposerBll.Noise_raw_count].append(df[column].max() - df[column].min())
                baseline_raw_count = df[column].mean()
                self.raw_count_datas[InterposerBll.Baseline_raw_count].append(baseline_raw_count)
                self.raw_count_datas[InterposerBll.Effective_dynamic_range].append(max_raw_count - baseline_raw_count)
                self.raw_count_datas[InterposerBll.Baseline].append(baseline_raw_count*1.0/max_raw_count)

            return self.raw_count_datas, InterposerBll.CS_KEYS

    # 分析计算采集到的raw count 数据
    # 参数：filename->写入文件路径
    # 参数: recount_count->处理记录总数据
    def raw_count_processing(self, filename, recount_count=50):
        try:
            # 1.计算电容值
            # 2.计算Nois raw count, baseline raw count, effective dynamic range
            # 3.计算第2步生成数据的电容值
            # 4.合并raw count和计算出的数据
            # 5.写入文件

            # 计算raw count记录数据(Noise raw count, baseline raw count, effective dynamic range, Baseline)
            self.raw_count_datas = {InterposerBll.Noise_raw_count: [], InterposerBll.Baseline_raw_count: [],
                                    InterposerBll.Effective_dynamic_range: [], InterposerBll.Baseline: []}
            # 对应raw_count_datas数据的电容值
            self.raw_count_Capacitance = {InterposerBll.Noise_raw_count: [], InterposerBll.Baseline_raw_count: [],
                                          InterposerBll.Effective_dynamic_range: [], InterposerBll.Baseline: []}

            records = self.r_cmdinfo.records
            l0_l11 = self.r_cmdinfo.L0_L11
            new_records = []
            if records is not None and len(records) > 0:
                if len(records) > recount_count:
                    records = records[0:recount_count]  # 只取recount_count条记录

                # 计算记录电容
                Capacitance_ls = self.to_CS(self.r_cmdinfo, records, l0_l11)
                # 计算Nois raw count, baseline raw count, effective dynamic range，baseline
                calculate_ls, cal_header = self.calculate(records)
                # 计算calculate_ls电容值
                # 计算Noise raw count电容值
                temp_key = InterposerBll.Noise_raw_count
                cs_ls = self.to_CS_diff(self.r_cmdinfo, [calculate_ls[temp_key]])
                if len(cs_ls) == 0:
                    temp_key = ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None", "None",
                                "None"]
                self.raw_count_Capacitance[temp_key] = cs_ls[0]
                # 计算Baseline_raw_count电容值
                temp_key = InterposerBll.Baseline_raw_count
                cs_ls = self.to_CS(self.r_cmdinfo, [calculate_ls[temp_key]], l0_l11)
                if len(cs_ls) == 0:
                    temp_key = ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None", "None",
                                "None"]
                self.raw_count_Capacitance[temp_key] = cs_ls[0]
                # 计算 Effective_dynamic_range电容值
                temp_key = InterposerBll.Effective_dynamic_range
                cs_ls = self.to_CS_diff(self.r_cmdinfo, [calculate_ls[temp_key]])
                if len(cs_ls) == 0:
                    temp_key = ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None", "None",
                                "None"]
                self.raw_count_Capacitance[temp_key] = cs_ls[0]
                # Baseline数据不需要计算电容值，返回空字符
                temp_key = InterposerBll.Baseline
                self.raw_count_Capacitance[temp_key] = [""]*12

                # 合并raw count 和 电容值
                for raw, capacitance in zip(records, Capacitance_ls):
                    ls = ['']
                    ls.extend(raw)
                    ls.extend(capacitance)
                    new_records.append(ls)

                # 合并2和3数据,并追加到new_records集合中 calculate_ls.keys()
                for key in cal_header:
                    data = [key]
                    data.extend(calculate_ls[key])
                    data.extend(self.raw_count_Capacitance[key])
                    new_records.append(data)

                # header = ["Noise_Raw_Count", "Baseline_Raw_Count", "Effevctive"]
                # i = 0
                # for cal, capacitance in zip(calculate_ls, calculate_Capacitance_ls):
                #     data = [header[i]]
                #     data.extend(cal)
                #     data.extend(capacitance)
                #     new_records.append(data)
                #     i += 1

                # 写入文件
                df = pandas.DataFrame(new_records)
                df.columns = ["", "L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11",
                                     "L0 Capacitance", "L1 Capacitance", "L2 Capacitance", "L3 Capacitance",
                                     "L4 Capacitance", "L5 Capacitance", "L6 Capacitance", "L7 Capacitance",
                                     "L8 Capacitance", "L9 Capacitance", "L10 Capacitance", "L11 Capacitance"]
                df.to_csv(filename, index=False, sep=',')
                return True, 'ok'
            else:
                return False, 'no ran count data'
        except Exception, ex:
            return False, "raw_count_processing -exception" + ex.message

    # 分析计算采集到的difference数据
    # 参数：filename->写入文件路径
    def difference_data_processing(self, filename):
        try:
            # 1.找到第1条有接触数据记录(diff > 0)，下面步骤都是从该位置计算
            # 2.开始计算每条电容值
            # 3.计算centroid数据
            # 4.找出第2条生成数据的每条最大电容值
            # 5.合并1-4生成的数据
            # 6.写入文件

            # difference_data_processing计算出的每条sensor最大电容值,touch saturation，centroid数据(触摸位置),
            # 根据Centroid_pos计算出的sensor 编号->格式：{"L0":[]...."L11":[]}
            self.difference_cal_datas = {InterposerBll.Differenve_Max_data: [],
                                         InterposerBll.Differenve_Max_Cap: [],
                                         InterposerBll.Touch_saturation: [],
                                         InterposerBll.Centroid_pos: [],
                                         InterposerBll.Sensor_NO: []}

            records = self.t_cmdInfo.records
            l0_l11 = self.t_cmdInfo.L0_L11
            new_records = []
            cal_records = []
            if records is not None and len(records) > 0:
                # 找到第1条diff>0的记录数据
                # for index, in zip(range(len(records)), records):
                for index in range(len(records)):
                    if sum(records[index]) > 0:
                        cal_records = records[index:]
                        break
                # 如果没有接触数据，将把全部数据计算分析
                if len(cal_records) == 0:
                    cal_records = records
                # 开始计算每条电容值
                Capacitance_ls = self.to_CS_diff(self.t_cmdInfo, cal_records)
                # 计算centroid数据(位置数据)以及sensor no 计算
                sensor_no_datas = []
                for data in cal_records:
                    centroid_pos = round(self.centroid(data), 3)
                    self.difference_cal_datas[InterposerBll.Centroid_pos].append(centroid_pos)
                    # sensor no ：转换centroid_pos 为1位小数，然后取整
                    sensor_no = int(round(centroid_pos))
                    sensor_no_datas.append(sensor_no)
                # sensor no 赋值
                self.difference_cal_datas[InterposerBll.Sensor_NO] = sensor_no_datas

                print self.difference_cal_datas[InterposerBll.Centroid_pos], 'centroid'
                # 找出第2步生成数据的每条最大电容值
                max_Capacitance_ls = []
                df = pandas.DataFrame(Capacitance_ls)
                header = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11"]
                df.columns = header
                for culumn in header:
                    max_Capacitance_ls.append(df[culumn].max())
                self.difference_cal_datas[InterposerBll.Differenve_Max_Cap] = max_Capacitance_ls
                # 计算toucha staurtion 数据=max diff/ ​Effective Dynamic Range
                df = pandas.DataFrame(cal_records)
                df.columns = header

                effective_ls = self.raw_count_datas[InterposerBll.Effective_dynamic_range]
                max_diff_ls = []
                for culumn in header:
                    max_diff_ls.append(df[culumn].max())
                self.difference_cal_datas[InterposerBll.Differenve_Max_data] = max_diff_ls
                print max_diff_ls, 'max diff'
                toucha_staurtion = []    # toucha staurtion 数据=max diff/ ​Effective Dynamic Range
                for max_diff, effective in zip(max_diff_ls, effective_ls):
                    toucha_staurtion.append(max_diff/effective)
                self.difference_cal_datas[InterposerBll.Touch_saturation] = toucha_staurtion
                # 合并diff数据和电容数据
                for diff, cap in zip(cal_records, Capacitance_ls):
                    ls = [""]
                    ls.extend(diff)
                    ls.extend(cap)
                    new_records.append(ls)

                # toucha_staurtion数据写入
                ls = ["touch saturation"]
                ls.extend(toucha_staurtion)
                ls.extend([""] * 12)
                new_records.append(ls)

                # 最大电容值追加到集合中
                ls =['max touch capacitance','','','','','','','','','','','','']
                ls.extend(max_Capacitance_ls)
                new_records.append(ls)
                # 写入文件
                df = pandas.DataFrame(new_records)
                df.columns = ["","L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11",
                                     "L0 Capacitance", "L1 Capacitance", "L2 Capacitance", "L3 Capacitance",
                                     "L4 Capacitance", "L5 Capacitance", "L6 Capacitance", "L7 Capacitance",
                                     "L8 Capacitance", "L9 Capacitance", "L10 Capacitance", "L11 Capacitance"]
                df.to_csv(filename, index=False, sep=',')
                return True, 'difference_data_processing ok'
            else:
                return False, 'no diffenece data'
        except Exception, ex:
            return False, "difference_data_processing -exception:"+ ex.message

    # 分析计算滚动采集到raw count 数据
    # 转换成difference数据
    # 参数：filename->写入文件路径
    def difference_rawcount_processing(self, filename):
        try:
            # 将滚动采集的raw count 转换成difference数据
            # 1.找到第1条有接触数据记录(diff > 0)，下面步骤都是从该位置计算
            # 2.开始计算每条电容值
            # 3.计算centroid数据
            # 4.找出第2条生成数据的每条最大电容值
            # 5.合并1-4生成的数据
            # 6.写入文件

            # difference_data_processing计算出的每条sensor最大电容值,touch saturation，centroid数据(触摸位置),
            # 根据Centroid_pos计算出的sensor 编号->格式：{"L0":[]...."L11":[]}
            self.difference_cal_datas = {InterposerBll.Differenve_Max_data: [],
                                         InterposerBll.Differenve_Max_Cap: [],
                                         InterposerBll.Touch_saturation: [],
                                         InterposerBll.Centroid_pos: [],
                                         InterposerBll.Sensor_NO: []}

            rawcount_records = self.r_cmdinfo.roll_records

            baseline_raw_count = self.raw_count_datas[InterposerBll.Baseline_raw_count]
            records = []
            # 转换成difference数据
            for rcd in rawcount_records:
                ls = [raw_a-raw_b if raw_a-raw_b >= 20 else 0 for raw_a, raw_b in zip(rcd, baseline_raw_count)]
                records.append(ls)

            l0_l11 = self.r_cmdinfo.L0_L11
            new_records = []
            cal_records = []
            if records is not None and len(records) > 0:
                # 找到第1条diff>0的记录数据
                # for index, in zip(range(len(records)), records):
                for index in range(len(records)):
                    if sum(records[index]) > 0:
                        cal_records = records[index:]
                        break
                # 如果没有接触数据，将把全部数据计算分析
                if len(cal_records) == 0:
                    cal_records = records
                # 开始计算每条电容值
                Capacitance_ls = self.to_CS_diff(self.r_cmdinfo, cal_records)
                # 计算centroid数据(位置数据)以及sensor no 计算
                sensor_no_datas = []
                for data in cal_records:
                    temp = self.centroid(data)
                    print temp
                    centroid_pos = round(temp, 2)
                    self.difference_cal_datas[InterposerBll.Centroid_pos].append(centroid_pos)
                    # sensor no ：转换centroid_pos 为1位小数，然后取整
                    sensor_no = int(round(centroid_pos))
                    sensor_no_datas.append(sensor_no)
                # sensor no 赋值
                self.difference_cal_datas[InterposerBll.Sensor_NO] = sensor_no_datas

                print self.difference_cal_datas[InterposerBll.Centroid_pos], 'centroid'
                # 找出第2步生成数据的每条最大电容值
                max_Capacitance_ls = []
                df = pandas.DataFrame(Capacitance_ls)
                header = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11"]
                df.columns = header
                for culumn in header:
                    max_Capacitance_ls.append(df[culumn].max())
                self.difference_cal_datas[InterposerBll.Differenve_Max_Cap] = max_Capacitance_ls
                # 计算toucha staurtion 数据=max diff/ ​Effective Dynamic Range
                df = pandas.DataFrame(cal_records)
                df.columns = header

                effective_ls = self.raw_count_datas[InterposerBll.Effective_dynamic_range]
                max_diff_ls = []
                for culumn in header:
                    max_diff_ls.append(df[culumn].max())
                self.difference_cal_datas[InterposerBll.Differenve_Max_data] = max_diff_ls
                print max_diff_ls, 'max diff'
                toucha_staurtion = []    # toucha staurtion 数据=max diff/ ​Effective Dynamic Range
                for max_diff, effective in zip(max_diff_ls, effective_ls):
                    toucha_staurtion.append(max_diff/effective)
                self.difference_cal_datas[InterposerBll.Touch_saturation] = toucha_staurtion
                # 合并diff数据和电容数据
                for diff, cap in zip(cal_records, Capacitance_ls):
                    ls = [""]
                    ls.extend(diff)
                    ls.extend(cap)
                    new_records.append(ls)

                # toucha_staurtion数据写入
                ls = ["touch saturation"]
                ls.extend(toucha_staurtion)
                ls.extend([""] * 12)
                new_records.append(ls)

                # 最大电容值追加到集合中
                ls =['max touch capacitance','','','','','','','','','','','','']
                ls.extend(max_Capacitance_ls)
                new_records.append(ls)
                # 写入文件
                df = pandas.DataFrame(new_records)
                df.columns = ["","L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11",
                                     "L0 Capacitance", "L1 Capacitance", "L2 Capacitance", "L3 Capacitance",
                                     "L4 Capacitance", "L5 Capacitance", "L6 Capacitance", "L7 Capacitance",
                                     "L8 Capacitance", "L9 Capacitance", "L10 Capacitance", "L11 Capacitance"]
                df.to_csv(filename, index=False, sep=',')
                return True, 'difference_data_processing ok'
            else:
                return False, 'no diffenece data'
        except Exception, ex:
            return False, "difference_data_processing -exception:"+ ex.message


def aaatest_tha(bll):
    bll.read_touch_data()


if __name__ == "__main__":
    import matplotlib

    # nois_raw_count = [4,26,15,13,11,12,13,14,22,16,29,5]
    bll = InterposerBll("COM19")

    bll.mcu_com.auto_connect(["COM19"])

    # datas = "27963, 3493, 3451, 3584, 3387, 3455, 3526, 3666, 3 3475, 3543, 3692, 3670, 3750, 3697, 3952, 3458"
    # bll.r_cmdinfo.todifferenceInfo(datas)

    bll.mcu_com.mcu_start()

    bll.mcu_com.init()
    # print bll.start_Haptics()
    print bll.stop_Haptics()
    # i命令调试
    print bll.get_facetoy_config()
    # print bll.start_Haptics()
    # print bll.current_Info.L0_L11

    # led测试
    # print bll.start_led(r='FF', b='FF', g='FF')
    # time.sleep(5)
    # print bll.start_led(r='00', b='00', g='00')  # 关

    # # raw count 调试
    # datas = bll.read_raw_count()
    # print bll.start_Haptics()
    # bll.raw_count_processing("aaa5.csv")
    # print bll.r_cmdinfo.VREF
    # print bll.r_cmdinfo.CSD_tuning_mode
    # print bll.r_cmdinfo.Scan_Resolution
    # print bll.r_cmdinfo.Sense_Clock_Frequency
    # print bll.r_cmdinfo.Modulation_Clock_Frequency
    # print bll.r_cmdinfo.Noise_Threshold
    # print bll.r_cmdinfo.Modulation_IDAC_Value
    # print bll.r_cmdinfo.Compensation_IDAC_Values
    # print bll.r_cmdinfo.prox
    # print bll.r_cmdinfo.L0_L11
    # print bll.raw_count_processing('a.csv')
    # print bll.raw_count_datas
    # print bll.raw_count_Capacitance
    #
    # t命令调试
    # print bll.start_t(), '开启t命令'            # 开启t命令
    # time.sleep(5)
    # import threading
    # th = threading.Thread(target=aaatest_tha, args=(bll,))
    # th.start()
    # time.sleep(2)
    # bll.stop_collect()
    # time.sleep(3)
    # print bll.difference_data_processing('b.csv')
    # print "Differenve_Max_data", bll.difference_cal_datas[bll.Differenve_Max_data]
    # print "Differenve_Max_Cap", bll.difference_cal_datas[bll.Differenve_Max_Cap]
    # print "Touch_saturation", bll.difference_cal_datas[bll.Touch_saturation]
    # print "Centroid_pos", bll.difference_cal_datas[bll.Centroid_pos]
    # print "Sensor_NO", bll.difference_cal_datas[bll.Sensor_NO]

    # print bll.mcu_com.close_up()
