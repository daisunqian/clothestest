#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   sqdai
@Contact :   654251408@qq.com
@Software:   PyCharm
@File    :   IQC.py
@Time    :   2019/4/11 13:10

'''
from FixtureControl.IJacquardTest import *
from Comm.Accelerometer import *
from Controller.MCUComm import *
from FixtureControl import APPConfigparse
import time
import threading
import datetime
import pandas
import numpy as np
import tkinter
from Comm.picture import Pictures
import json

class IQC_tester(IJacquardTest):
    def __init__(self, config, limit_config):
        super(IQC_tester, self).__init__()
        self.config_obj = config  # 配置文件
        self.limit_config = limit_config  # 门限判定配置对象(包含所有配置信息)
        self.haptics_probe = None  # 振动测试对象
        self.mcu = None  # mcu对象（采集产品数据）
        self.test_mode = 1  # 测试模式：1=滚动测试模式，2=矩形面压模式
        self.min_sensor_NO = self.config_obj.min_sensor_NO
        self.max_sensor_NO = self.config_obj.max_sensor_NO
        self.wait_time_out = self.config_obj.wait_time_out
        self._diff_state = False
        self._diff_th = None
        Pictures.getpicture(os.getcwd() + "\\resource")
        if isinstance(self.config_obj, APPConfigparse.APPConfigparse):
            global DEBUG
            DEBUG = self.config_obj.Debug
            self.test_mode = self.config_obj.Test_mode

    # 创建日志对象
    # print_flag=True打印到控制台
    def _createLogger(self, filename=None, print_flag=False, level='debug'):
        import datetime
        # 当前执行路径
        if filename is None or len(filename) == 0:
            if isinstance(self.config_obj, APPConfigparse.APPConfigparse):
                ph = self.config_obj.App_log_dir
                if ph is not None and len(ph) > 0:
                    log_dir = ph
                if os.path.exists(log_dir) is False:
                    os.mkdir(log_dir)
                filename = "{0}\{1}.log".format(log_dir, datetime.datetime.now().strftime('%Y%m%d'))
            else:
                return super(IQC_tester, self)._createLogger()
        else:
            return super(IQC_tester, self)._createLogger()
        return Logger(filename, print_flag=print_flag, level=level)

    # 初始化对象,检测连接
    # auto = True自定查找端口
    # auto = True时，port_list端口集合有效
    def check_connect(self, auto=False, port_list=None):
        init_st = [(False, 'no init')] * 1
        if isinstance(self.config_obj, APPConfigparse.APPConfigparse):
            init_st[0] = self._mcu(auto, port_list)
        else:
            self._on_display_msg('check_connect', 'app config object not init', False)
        self.connected_finished.emit(init_st)
        return init_st

    # 振动测试对象初始化
    def _haptics_probe(self, auto=False, port_list=None):
        try:
            msg = ''
            status = True
            self.haptics_probe = AccelerometerBll(self.config_obj.Acc_port, self.config_obj.Acc_braudate)
            status, msg = self.haptics_probe.auto_connect([self.config_obj.Acc_port])    # 检测配置文件端口
            if status is True and auto is True and port_list is not None and len(port_list) > 0:
                port_list.remove(self.config_obj.Acc_port)

            if auto and status is False:
                status, msg = self.haptics_probe .auto_connect(port_list)
                if status:
                    self.config_obj.Acc_port = msg
                    port_list.remove(msg)    # 成功，返回port

            if status:
                msg = 'Acc init OK'
            else:
                msg = 'Acc init fail'
            return status, 'acc '+self.config_obj.Acc_port
        except Exception, ex:
            if self.haptics_probe is not None:
                self.haptics_probe.stop_read()
            msg = 'acc init exception:' + ex.message
            status = False
            return False, 'acc init exception'
        finally:
            # self.display_msg.emit(msg, status)
            self._on_display_msg('_haptics_probe', msg, status)

    # mcu初始化
    def _mcu(self, auto=False, port_list=None):
        try:
            msg = ''
            status = True
            self.mcu = InterposerBll(self.config_obj.MCU_Port, self.config_obj.MCU_braudate)
            if self.config_obj.mcu_type == 1:
                status, msg = self.mcu.mcu_com.auto_connect([self.config_obj.MCU_Port])  # 检测配置文件端口
                if status is True and auto is True and port_list is not None and len(port_list) > 0:
                    port_list.remove(self.config_obj.MCU_Port)

                # self.mcu = InterposerBll(self.config_obj.MCU_Port, self.config_obj.MCU_braudate)
                if auto and status is False:
                    status, msg = self.mcu.mcu_com.auto_connect(port_list)
                    if status:
                        self.config_obj.MCU_Port = msg
                        port_list.remove(msg)  # 成功，返回port
                else:
                    msg = 'MCU init ok'
            return status, 'MCU '+self.config_obj.MCU_Port
        except Exception, ex:
            if self.mcu is not None:
                self.mcu.ClosePort()
                msg = 'MCU init exception' + ex.message
            status = False
            return False, 'MCU init exception'
        finally:
            # self.display_msg.emit(msg, status)
            self._on_display_msg('_mcu', msg, status)


 # 启动测试
    def start_test(self):
        print 3333
        try:
            self._testing = True
            self.current_test_result = True
            self.start_time = datetime.datetime.now()  # 测试开始时间
            self.current_sn = ''
            test_status = True
            if DEBUG:
                self.test_start.emit()
                for i in range(0, 20):
                    self.item_start.emit("test{0}".format(i))
                    time.sleep(0.5)
                    if i == 20:
                        test_status = False
                        self.item_end.emit("test{0}".format(i), False, str(i), 'Fail')
                    else:
                        self.item_end.emit("test{0}".format(i), True, str(i), 'pass')
                self.current_test_result = test_status
                # self.test_end.emit(self.current_sn, test_status)
            else:
                if self.check_Fixture():
                    # test_exit = self.config_obj.test_exit
                    self._on_test_start()
                    # 1.初始化
                    test_status = self._test_init()
                    check_dut_status = False
                    # 2. 读出dut信息
                    if test_status:
                        check_dut_status = self._check_dut()

                    else:
                        self.current_test_result = False
                    # 3. 采集dut raw count 数据
                    if check_dut_status:
                        test_status = self._check_raw_count()
                        if test_status is False:
                            self.current_test_result = False
                    else:
                        test_status = False
                        self.current_test_result = False

                    # 3.5采集baseline_row_count
                    if check_dut_status and self._testing and test_status:
                        test_status = self.Baseline_raw_count()
                        if test_status is False:
                            self.current_test_result = False
                    else:
                        test_status = False
                        self.current_test_result = False

                    # 4. 滚压测试(电机下压，同时检测压力是否在范围内，压力到达门限,停止下压，进行滚动测试)
                    if check_dut_status and self._testing and test_status:

                        test_status = self._roll_test()
                    else:
                        test_status = False
                        self.current_test_result = False

                    if test_status is False:
                        self.current_test_result = False

                    # 5. 振动测试
                    if check_dut_status and self._testing and test_status:
                        test_status = self._vibration_test()
                        print test_status,"2321"
                        if not test_status:
                            self.current_test_result = False
                        # if test_status is False:
                        #     self.current_test_result = False

                    if self.current_test_result:
                        self._test_finished()
                    else:
                        self.current_test_result = False
                        # 失败复位
                        self.mcu.stop_Haptics()
                        self._on_display_msg('vibration_test', 'test fail', False)

                else:
                    self.current_test_result = False

            # self.test_end.emit(self.current_sn, test_status if isinstance(test_status, bool) else False)
            self._on_test_end(self.current_sn, self.current_test_result)
            self.end_time = datetime.datetime.now()  # 测试结束时间
            self._testing = False

            return test_status
        finally:
            self.mcu.stop_collect()

    # 单步执行测试,主要应用调试demo使用
    # step 测试步骤
    # step = 1->check_Fixture          治具检测
    # step = 2->_pressure_test         面压测试
    # step = 3->_roll_test             滚压测试
    # step = 4->_vibration_test        振动测试


    def _check_raw_count(self):
        # 0. 采集dut非接触时的raw count数据
        test_status = self._collect_raw_count()
        # 进行数据判定(衣服klsensor只有10条,从1到10)
        if test_status:
            # 1.判定Noise capacitance
            status1 = self._Noise_capacitance()
            # 2.判定Baseline 百分比
            status2 = self._Baseline()
            # 3.判定Effective Dynamic Range Capacitance
            status3 = self._edr_Capacitance()
            test_status = status1 and status2 and status3
            print test_status,"444444444"
        return test_status


    # 滚动测试
    def _roll_test(self, dut=True):
        try:
            # 3开启t命令
            test_status = True
            if test_status:
                test_status = self._open_diff()
            if test_status:
                self.getdata()
                test_status = self._on_manual_window(u'检验传感器部分',u'请在规定的时间内按下句柄',)
                self._diff_th.join()
                print "self._diff_state",self._diff_state
                #test_status = self._roll_check_difference()

            return self._diff_state

        except Exception, ex:
            test_status = False
            msg = 'exception:'+str(ex)
            return test_status

        # finally:
        #     self._on_item_end(self.current_item, test_status, str(test_status), msg)
        #     self._on_display_msg('roll_test', msg, test_status)

    # 振动测试
    def _vibration_test(self):
   #     try:
            print "_vibration_test"
            # time.sleep(3)
            self.current_item = 'vibration_test'
            self._on_item_start(self.current_item)
            msg = ''
            test_status = self.mcu.start_Haptics()

            test_status = self._on_manual_window2("", "")
            msg = 'vibration test ok' if test_status else 'vibration test fail'
            self._on_item_end(self.current_item, test_status, str(test_status), msg)
            self._on_display_msg('vibration_test', msg, test_status)
            print test_status,"&*&&"
            return test_status
        # except Exception, ex:
        #     test_status = False
        #     msg = 'exception:'+str(ex)
        #     return test_status
        # finally:
        #     self._on_item_end(self.current_item, test_status, str(test_status), msg)
        #     self._on_display_msg('vibration_test', msg, test_status)

        #return False

    # 测试结束，正常复位
    def _test_finished(self):
        self.mcu.stop_Haptics()
        return False

    def _test_init(self):
        return True

    # 采集dut i 命令数据
    def _check_dut(self):
        try:
            self.current_sn = ''
            self.current_item = 'check_dut'
            self._on_item_start(self.current_item)
            msg = ''
            status = False
            if isinstance(self.mcu, InterposerBll):
                if self.config_obj.mcu_type == 2:
                    status = self.mcu.mcu_com.init()
                    if status is False:
                        msg = self.mcu.mcu_com.message
                        self._on_display_msg('_check_dut->mcu_com.init()', msg, status)
                else:
                    status = self.mcu.mcu_com.mcu_start()
                    if status is False:
                        msg = self.mcu.mcu_com.message
                        self._on_display_msg('_check_dut->mcu_com.mcu_start()', msg, status)

                # 读出产品的基本信息
                status, msg = self.mcu.get_facetoy_config()
                if status:
                    self.current_sn = self.mcu.current_Info.Manufacturing_ID.strip()
                    print self.current_sn
                    self._on_read_sn(self.current_sn)
                    file_path = self.get_save_dir() + "\\" + 'i_command_info.txt'
                    # 将数据写入到文件中
                    with open(file_path, 'w') as fp:
                        fp.write(self.mcu.current_Info.command_datas)
            else:
                msg = 'mcu objec is not InterposerBll'
            return status
        except Exception, ex:
            msg = "exception" + ex.message
            status = False
            return status
        finally:
            print 'error'
            self._on_item_end(self.current_item, status, self.current_sn, msg)
            self._on_display_msg('_check_dut', msg, status)


 # 检测治具是否有报警, 有报警返回false,否则返回true
    def check_Fixture(self):
        return True


    # no touch时采集raw count
    def _collect_raw_count(self):
        try:
            self.current_item = 'collect_raw_count'
            self._on_item_start(self.current_item)
            msg = ''
            status = False
            if isinstance(self.mcu, InterposerBll):
                # 采集raw count 数据
                status, msg = self.mcu.read_raw_count()
                if status:
                    # 数据处理
                    import datetime
                    file_path = self.get_save_dir() + "\\" + self.current_sn + \
                                "_raw_count_"+datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"
                    status, msg = self.mcu.raw_count_processing(file_path)

                    # r命令信息写入文件
                    file_path = self.get_save_dir() + "\\" + 'r_command_info.txt'
                    with open(file_path, 'w') as fp:
                        fp.write(self.mcu.r_cmdinfo.command_datas)
                    if status:
                        msg = 'collect raw count ok'
            else:
                msg = 'mcu objec is not InterposerBll'
            return status
        except Exception, ex:
            msg = "exeption" + ex.message
            status = False
            return status
        finally:
            self._on_item_end(self.current_item, status, self.current_sn, msg)
            self._on_display_msg('_collect_raw_count', msg, status)

 # _Noise_capacitance 判定
    def _Noise_capacitance(self):
        test_status = True           # 只要有一个失败，都是失败
        limit_str = "x<={0}pF".format(self.limit_config.Noise_capacitance_max)
        Noise_capacitance = self.mcu.raw_count_Capacitance[self.mcu.Noise_raw_count]
        if Noise_capacitance is None or len(Noise_capacitance) == 0:
            Noise_capacitance = ["None"] * 12

        # for i in range(1, 11):
        for i in range(self.min_sensor_NO, self.max_sensor_NO):
            status = False
            msg = 'fail'
            if isinstance(Noise_capacitance[i], str):
                status = False
                test_status = False
                msg = "Noise_capacitance is None"
            else:
                if Noise_capacitance[i] <= self.limit_config.Noise_capacitance_max:
                    status = True
                    msg = "Noise_capacitance <= {0}".format(self.limit_config.Noise_capacitance_max)
                else:
                    test_status = False
                    status = False
                    msg = "Noise_capacitance > {0}".format(self.limit_config.Noise_capacitance_max)
            self._on_item_end("L{0} noise capacitance".format(i), status, str(Noise_capacitance[i]), msg, limit_str)
        self._on_display_msg("_Noise_capacitance", msg, test_status)
        return test_status



    # 判定baseline数
    def _Baseline(self):
        test_status = True  # 只要有一个失败，都是失败
        baseline = self.mcu.raw_count_datas[self.mcu.Baseline]
        min_value = self.limit_config.Baseline_min
        max_value = self.limit_config.Baseline_max
        limit_str = "{0}%<x<{1}%".format(min_value*100, max_value*100)
        if baseline is None or len(baseline) == 0:
            baseline = ["None"] * 12

        # for i in range(1, 11):
        for i in range(self.min_sensor_NO, self.max_sensor_NO):
            status = False
            msg = 'fail'
            if isinstance(baseline[i], str):
                status = False
                test_status = False
                msg = "baseline is None"
            else:
                status = baseline[i] > min_value and  baseline[i] < max_value
                if status:
                    msg = "{0}<baseline<{1}".format(min_value, max_value)
                else:
                    test_status = False
                    msg = 'baseline not in the range'
            self._on_item_end("L{0} baseline".format(i), status, "{0}%".format(round(baseline[i]*100, 3)), msg, limit_str)
        self._on_display_msg("_Baseline", msg, test_status)
        return test_status


    # 判定Effective Dynamic Range Capacitance
    def _edr_Capacitance(self):
        test_status = True  # 只要有一个失败，都是失败
        edr_Capacitance = self.mcu.raw_count_Capacitance[self.mcu.Effective_dynamic_range]
        min_value = self.limit_config.Effective_Dynamic_Range_min
        limit_str = "x>={0}pF".format(min_value)
        if edr_Capacitance is None or len(edr_Capacitance) == 0:
            edr_Capacitance = ["None"] * 12

        # for i in range(1, 11):
        for i in range(self.min_sensor_NO, self.max_sensor_NO):
            status = False
            msg = 'fail'
            if isinstance(edr_Capacitance[i], str):
                status = False
                test_status = False
                msg = "Effective_dynamic_range is None"
            else:
                status = edr_Capacitance[i] >= min_value
                if status:
                    msg = "Effective_dynamic_range>={0}".format(min_value)
                else:
                    test_status = False
                    msg = "Effective_dynamic_range<{0}".format(min_value)
            self._on_item_end("L{0} Effective_dynamic_range".format(i), status, str(edr_Capacitance[i]), msg, limit_str)
        self._on_display_msg("_edr_Capacitance", msg, test_status)
        return test_status

    # 采集并验证difference数据---已修改，还未验证---liyunhe
    def _roll_check_difference(self):
        try:
            self._diff_state = False
            self.current_item = 'check_difference_step'
            # self._on_item_start(self.current_item)
            test_status = True
            subordinate = self.config_obj.Roll_subordinate
            pos = self.config_obj.Roll_pos
            # 开始采集dut difference数据
            self.mcu.mcu_com.Start_T_Collect()
            raed_str = ''
            i = 1
            st = time.time()
            while time.time() - st <= self.wait_time_out:
                # raed_str += self.mcu.mcu_com.Read_Buff()
                # print raed_str
                rdstr = self.mcu.mcu_com.Read_Buff()
                if len(rdstr) == 0:
                    time.sleep(0.01)
                    continue
                raed_str += rdstr
                self._on_touch_diffenrence(rdstr)
            try:
                self.mcu.mcu_com.ClosePort()
            except:
                pass

            try:
                file_path = self.get_save_dir() + "\\" + 'roll_t.txt'
                with open(file_path, 'w') as fp:
                    fp.write(raed_str)
            except Exception,ex:
                pass

            self.mcu.t_cmdInfo.to_touch_diff(raed_str)

            #  进行数据处理
            file_path = self.get_save_dir() + "\\" + self.current_sn + \
                        "differnece_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"

            test_status,msg = self.mcu.difference_data_processing(file_path)

            # 数据判定
            # 1. Max Touch Capacitance判定
            status1 = self._max_touch_cap()
            # 2. Touch Saturation 判定
            status2 = self._touch_Saturations()
            # 3. 触摸位置判定
            status3 = True

            test_status = status1 and status2 and status3
            self._diff_state = test_status
            if test_status:
                msg = "check difference step ok"
            else:
                msg += ",check difference step fail"

            self._on_item_end(self.current_item, test_status, str(test_status), msg)
            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status
        # finally:
        #     self.current_item = 'check_difference_step'
        #     self._on_item_end(self.current_item, test_status, str(test_status), msg)
        #     self._on_display_msg('_roll_check_difference', msg, test_status)

    # 判断baseline raw count 的电容值
    def Baseline_raw_count(self):
        test_status = True
        Baseline_raw_count = self.mcu.raw_count_Capacitance[self.mcu.Baseline_raw_count]
        limitdata = self.limit_config.Baseline_raw_count
        limit = json.loads(limitdata)
        # print type(limit)
        # print limit['L0']['max']

        if Baseline_raw_count is None or len(Baseline_raw_count) == 0:
            Baseline_raw_count = ["None"] * 12
        for i in range(self.min_sensor_NO, self.max_sensor_NO):
            status = False
            msg = 'fail'
            limitfrist = "L{0}".format(i)
            # print limitfrist
            # print limit[limitfrist]['max']
            max_value = limit[limitfrist]['max']
            min_value = limit[limitfrist]['min']
            limit_str = "{0}=<x=<{1}".format(min_value, max_value)
            if isinstance(Baseline_raw_count[i], str):
                status = False
                test_status = False
                msg = "Baseline_raw_count is None"
            else:
                status = Baseline_raw_count[i] >= min_value and  Baseline_raw_count[i] <= max_value
                if status:
                    msg = "{0}=<Baseline_raw_count=<{1}".format(min_value, max_value)
                else:
                    test_status = False
                    msg = 'Baseline_raw_count not in the range'
            self._on_item_end("L{0} Baseline_raw_count".format(i), status, "{0}".format(round(Baseline_raw_count[i], 3)), msg, limit_str)
        self._on_display_msg("Baseline_raw_count", msg, test_status)
        return test_status






    # touch 时采集diff 数据
    # 该操作启动线程采集，必须调用stop 退出采集
    def _collect_diff_asy(self):
        try:
            # self.current_item = 'collect_difference_asy'
            # self._on_item_start(self.current_item)
            msg = ''
            status = False
            if isinstance(self.mcu, InterposerBll):
                # 采集difference数据
                status, msg = self.mcu.read_touch_data()
                # status = self.mcu.collect_raw_count()
                if status:
                    msg = 'collect difference data ok'
            else:
                msg = 'mcu objec is not InterposerBll'
            return status
        except Exception, ex:
            msg = "exeption" + ex.message
            status = False
            return status
        finally:
            # self.current_item = 'collect_difference_asy'
            # self._on_item_end(self.current_item, status, str(status), msg)
            self._on_display_msg('_collect_diff_asy', msg, status)

    # 开始t命令
    def _open_diff(self):
        try:
            # self.current_item = 'open_difference'
            # self._on_item_start(self.current_item)
            msg = ''
            status = False
            valuse_str = ''
            if isinstance(self.mcu, InterposerBll):
                # 采集raw count 数据
                status, msg = self.mcu.start_t()
                if status:
                    valuse_str = self.mcu.t_cmdInfo.collect_cmd_info
                    # r命令信息写入文件
                    file_path = self.get_save_dir() + "\\" + 't_command_info.txt'
                    with open(file_path, 'w') as fp:
                        fp.write(self.mcu.t_cmdInfo.collect_cmd_info)
                    msg = 'open difference command ok'
            else:
                msg = 'mcu objec is not InterposerBll'
            return status
        except Exception, ex:
            msg = "exeption" + ex.message
            status = False
            return status
        finally:
            # self._on_item_end(self.current_item, status, valuse_str, msg)
            self._on_display_msg('_open_diff', msg, status)

    # touch 时采集diff 数据
    # 该操作启动线程采集，必须调用stop 退出采集
    def _collect_diff(self):
        th = threading.Thread(target=self._collect_diff_asy)
        th.setDaemon(True)
        th.start()
        return True

    # 停止采集diff 数据
    def _stop_collect_diff(self):
        try:
            self.current_item = 'stop_collect_difference'
            self._on_item_start(self.current_item)
            msg = ''
            status = False
            if isinstance(self.mcu, InterposerBll):
                self.mcu.stop_collect()
                msg = 'collect stop'
                status = True
                time.sleep(1)
            else:
                msg = 'mcu objec is not InterposerBll'
            return status
        except Exception, ex:
            msg = "exeption" + ex.message
            status = False
            return status
        finally:
            self.current_item = 'stop_collect_difference'
            self._on_item_end(self.current_item, status, self.current_sn, msg)
            self._on_display_msg('_stop_collect_diff', msg, status)


    #  Max Touch Capacitance判定
    def _max_touch_cap(self):
        test_status = True             # 是要有一个失败都是失败
        max_touch_cap = self.mcu.difference_cal_datas[self.mcu.Differenve_Max_Cap]
        min_value = self.limit_config.Max_Touch_Capacitance_min
        max_value = self.limit_config.Max_Touch_Capacitance_max
        limit_str = "{0}pF<= x <={1}pF".format(min_value, max_value)
        if max_touch_cap is None or len(max_touch_cap) == 0:
            max_touch_cap = ["None"] * 12

        # for i in range(1, 11):
        for i in range(self.min_sensor_NO, self.max_sensor_NO):
            status = False
            msg = 'fail'
            if isinstance(max_touch_cap[i], str):
                status = False
                test_status = False
                msg = "max_touch is None"
            else:
                status = max_touch_cap[i] >= min_value and max_touch_cap[i] <= max_value
                if status:
                    msg = "{0}<=max_touch>={1}".format(min_value, max_value)
                else:
                    test_status = False
                    msg = "max_touch <{0} or max_touch > {1}".format(min_value, max_value)
            self._on_item_end("L{0} max_touch".format(i), status, str(max_touch_cap[i]), msg, limit_str)
        return test_status

    # Touch Saturation 判定
    def _touch_Saturations(self):
        test_status = True  # 是要有一个失败都是失败
        touch_Saturation = self.mcu.difference_cal_datas[self.mcu.Touch_saturation]
        # min_value = self.limit_config.Touch_Saturation_min
        max_value = self.limit_config.Touch_Saturation_max
        limit_str = "x<{0}%".format(max_value*100)
        if touch_Saturation is None or len(touch_Saturation) == 0:
            touch_Saturation = ["None"] * 12

        # for i in range(1, 11):
        for i in range(self.min_sensor_NO, self.max_sensor_NO):
            status = False
            msg = 'fail'
            if isinstance(touch_Saturation[i], str):
                status = False
                msg = "touch_Saturation is None"
                test_status = False
            else:
                status = touch_Saturation[i] < max_value
                if status:
                    msg = "touch_Saturation<{0}".format(max_value)
                else:
                    msg = 'touch_Saturation not in the range'
                    test_status = False
            self._on_item_end("L{0} touch_Saturation".format(i), status, "{0}%".format(round(touch_Saturation[i]*100, 3)), msg, limit_str)
        return test_status


    def show(self):
        root = tkinter.Tk()
        root.title("数据采集倒计时窗口")
        root['width'] = 400
        root['height'] = 300
        root.resizable(False, False)

        richText = tkinter.Text(root, width=380)
        richText.place(x=10, y=10, width=380, height=230)
        richText.insert('0.0', '请把句柄按下压到布料上')
        lbTime = tkinter.Label(root, fg="red", anchor="w")
        lbTime.place(x=10, y=250, width=150)

        def autoclose():
            for i in range(10):
                lbTime['text'] = '距离窗口关闭还有{}秒'.format(10 - i)
                time.sleep(1)
            root.destroy()

        t = threading.Thread(target=autoclose)
        t.start()
        root.mainloop()
        t.join()

    def getdata(self):
        self._diff_th = threading.Thread(target=self._roll_check_difference)
        self._diff_th.start()

