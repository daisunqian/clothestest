# -*- coding=utf-8 -*-

from FixtureControl.IJacquardTest import *
from Comm.LoadCellData import LocalCell
from Comm.Accelerometer import *
from Controller.MCUComm import *
from Comm.MoonsController import MoonsController
from FixtureControl import APPConfigparse
from Controller.KMLFATPIO import KMLFATPIO
import time
import threading
import datetime
import pandas
import numpy as np


DEBUG = False              # true使用测试代码执行
# 电机运动参数
SPEED = 2000                  # 下压和上压运动速度
ROLL_SPEED = 500             # 滚动运动速度
ACCELEROMETER = 300          # 加速度
DECELERATION = 300           # 减速度
RATIO = 1                    # 比例
MAX_N = 6                      # 报警最大N，默认6N, 达到这个值将停止一切电机运动


# 衣服测试
class KML_tester_base(IJacquardTest):

    def __init__(self, config, limit_config):
        super(KML_tester_base, self).__init__()
        self.config_obj = config                         # 配置文件
        self.limit_config = limit_config                 # 门限判定配置对象(包含所有配置信息)
        self.kmlio = None                                # io
        self.loadcell = None                             # loadcell对象
        self.haptics_probe = None                        # 振动测试对象
        self.mcu = None                                  # mcu对象（采集产品数据）
        self.moon_motor = None                           # 步进电机对象
        self.test_mode = 1                               # 测试模式：1=滚动测试模式，2=矩形面压模式
        self.min_sensor_NO = 1
        self.max_sensor_NO = 11
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
                return super(KML_tester_base, self)._createLogger()
        else:
            return super(KML_tester_base, self)._createLogger()
        return Logger(filename, print_flag=print_flag, level=level)

    # 初始化对象,检测连接
    # auto = True自定查找端口
    # auto = True时，port_list端口集合有效
    def check_connect(self, auto=False, port_list=None):
        init_st = [(False, 'no init')] * 5
        if isinstance(self.config_obj, APPConfigparse.APPConfigparse):
            init_st[0] = self._init_io(auto, port_list)
            init_st[1] = self._loadcell(auto, port_list)
            init_st[2] = self._haptics_probe(auto, port_list)
            init_st[3] = self._mcu(auto, port_list)
            init_st[4] = self._moon_motor(auto, port_list)
        else:
            self._on_display_msg('check_connect', 'app config object not init', False)
        self.connected_finished.emit(init_st)
        return init_st

    # 检测脚踏板是否已踩下(1秒都检测到踩下信号，表示真的踩下，否则认为是误触发)
    def _check_foot_switch(self, check_time=0.5):
        # 设备没有安装,暂时屏蔽
        start_time = time.time()
        while True:
            if self.kmlio.get_foot_switch()[0] == 0:
                return False
            if time.time() - start_time >= check_time:
                break
        return True

    # 抓紧产品,true成功，否则失败
    def _stretch_relax(self):
        if self.kmlio.set_stretch_relax(0):
            if self.kmlio.get_claw_clamp(tovalue=0, wait=True, timeout=5)[0] == 1:
                return True
        self._on_display_msg("_stretch_relax", "set_stretch_relax fail")
        return False

    # 张紧产品,true成功，否则失败
    def _stretch_tensioning(self):
        if self.kmlio.set_stretch_tensioning(0):
            if self.kmlio.get_stretch_tensioning(tovalue=1, wait=True, timeout=5)[0] == 1:
                return True
        self._on_display_msg("_stretch_tensioning", "set_stretch_tensioning fail")
        return False

    # 加速度无杆气缸电磁阀上
    def _accelerated_up(self):
        try:
            test_status = True
            msg = ''
            status, set_data = self.kmlio.set_accelerated_up(0)
            if status is True:
                value, data = self.kmlio.get_accelerated_up(0, True)
                if value != 1:
                    test_status = False
                    msg = 'get_accelerated_up fail'
            else:
                test_status = False
                msg = 'set_accelerated_up fail'

            return test_status, msg
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status, msg
        finally:
            self._on_display_msg('_accelerated_up', msg, test_status)

    # 检测加速无杆气缸是否在上
    # true在上，否则失败
    def _check_accelerated_up(self, wait=False):
        try:
            test_status = True
            msg = 'accelerated_up'
            value, data = self.kmlio.get_accelerated_up(0, wait)
            if value != 1:
                test_status = False
                msg = 'check accelerated_up fail'

            return test_status, msg
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status, msg
        finally:
            self._on_display_msg('_check_accelerated_up', msg, test_status)

    # 检测start button 按下信号,true已按下，否则未按下
    def _checkt_start_signal(self):
        if self.kmlio.get_start_button1()[0] == 1 and self.kmlio.get_start_button2()[0] == 1:
            return True
        else:
            return False

    # 检测设备开始信号
    def check_signal(self):
        if DEBUG:
            # 调试模式
            self._monitor = True
            time.sleep(2)
            # self.signal_happen.emit(START_SIGNAL)
            self._on_signal_happen(START_SIGNAL)
            # 启动测试
            self.start_test()
        else:
            if self.kmlio is not None:
                self._check_io_signal = True
                # 检测到复位按键被按下
                if self.kmlio.get_reset_button()[0] == 1:
                    time.sleep(0.5)
                    if self.kmlio.get_reset_button()[0] == 1:
                        self.kmlio.set_reset_lamp(0)
                        self._check_io_signal = False
                        self._testing = False
                        st = time.time()
                        while time.time() - st <= 30:
                            if self.kmlio.get_reset_button()[0] == 0:
                                self._on_signal_happen(RESET_SIGNAL)
                                break
                            else:
                                time.sleep(0.1)

                # 检测到e-stop按键被按下
                if self.kmlio.get_E_Stop()[0] == 1:
                    self._check_io_signal = False
                    self._testing = False
                    self._on_signal_happen(E_STOP_SIGNAL)

                # # 1. 检测治具是否有报警现象
                # if self._check_io_signal:
                #     self._check_io_signal = self.check_Fixture()

                # 2.关闭启动灯，提示按启动键开始测试
                if self._check_io_signal:
                    self.kmlio.set_start_lamp(1)
                # 3. 检测踏板踩踏信号
                if self._check_io_signal:
                    self._check_io_signal = self._check_foot_switch()
                    if self._check_io_signal:
                        self._check_io_signal = self._stretch_relax()
                        self.kmlio.set_start_lamp(0 if self._testing else 1)  # 打开启动灯，提示按启动键开始测试

                # 4. 检测startbutton信号, 并且没有在测试产品,开始测试
                while self._check_io_signal and self._testing is False:
                    if self._checkt_start_signal():
                        self.kmlio.set_start_lamp(0)
                        # self.signal_happen.emit(START_SIGNAL)
                        self._on_signal_happen(START_SIGNAL)
                        # 启动测试
                        self.start_test()
                        # th = threading.Thread(target=self.start_test)
                        # th.setDaemon(True)
                        # th.start()
                        break

                    # 检测到复位按键被按下
                    if self.kmlio.get_reset_button()[0] == 1:
                        time.sleep(0.5)
                        if self.kmlio.get_reset_button()[0] == 1:
                            self._testing = False
                            self.kmlio.set_reset_lamp(0)
                            st = time.time()
                            while time.time() - st <= 30:
                                if self.kmlio.get_reset_button()[0] == 0:
                                    self._on_signal_happen(RESET_SIGNAL)
                                    break
                                else:
                                    time.sleep(0.1)
                            # self._on_signal_happen(RESET_SIGNAL)
                            break

                    # 检测到e-stop按键被按下
                    if self.kmlio.get_E_Stop()[0] == 1:
                        self._testing = False
                        # self.signal_happen.emit(E_STOP_SIGNAL)
                        self._on_signal_happen(E_STOP_SIGNAL)
                        break

                    time.sleep(1)
            else:
                # self.display_msg.emit('IO object not init', False)
                self._on_display_msg('check_signal', 'IO object not init', False)
                self._testing = False
                time.sleep(1)

    # 停止检测信号
    def stop_check(self):
        self._monitor = False

    # 启动测试
    def start_test(self):
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
                        if test_status is False:
                            self.current_test_result = False

                    if self.current_test_result:
                        # test_status = self._vibration_test()
                        # 7. 测试结束
                        self._test_finished()
                    else:
                        self.current_test_result = False
                        # 失败复位
                        self._on_display_msg('start_test', 'test fail, start reset', False)
                        self.reset()
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
    def test_step(self, step):
        try:
            self._testing = True
            if step == 1:
                return self.check_Fixture() and self._test_init()

            # 夹紧 & 张紧
            if step == 2:
                return self._stretch_relax() and self._stretch_tensioning()

            if step == 3:
                return self._roll_test(False)

            if step == 4:
                return self._vibration_test()

            return False
        finally:
            self._testing = False

    # 复位
    def reset(self):
        raise NotImplementedError()

    # 设备回原点
    def backhome(self):
        raise NotImplementedError()

    # 检测治具是否有报警, 有报警返回false,否则返回true
    def check_Fixture(self):
        result = self.kmlio.get_roll_warning()
        if result[0] == 1:
            self.display_msg.emit('roll warning result = ' + str(result), False)
            return False

        result = self.kmlio.get_loadcell_warning()
        if result[0] == 1:
            self.display_msg.emit('loadcell warning = ' + str(result), False)
            return False

        result = self.kmlio.get_safty_raster()
        if result[0] == 1:
            self.display_msg.emit('safty door not close = ' + str(result), False)
            return False

        return True

    # 测试初始化
    def _test_init(self):
        return False

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
                    self.current_sn = self.mcu.current_Info.Manufacturing_ID
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
            self._on_item_end(self.current_item, status, self.current_sn, msg)
            self._on_display_msg('_check_dut', msg, status)

    #  检测raw count 数据
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
        return test_status

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
            self.current_item = 'open_difference'
            self._on_item_start(self.current_item)
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
            self._on_item_end(self.current_item, status, valuse_str, msg)
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

    # 采集并验证difference数据
    def _roll_check_difference(self):
        try:
            self.current_item = 'check_difference_step'
            self._on_item_start(self.current_item)
            test_status = True
            slave = self.config_obj.Roll_slave
            pos = self.config_obj.Roll_pos
            # 采集dut diff数据
            # self._collect_diff()
            test_status = self._Moveline(slave, pos, ROLL_SPEED, False)
            raed_str = ''
            while True:
                # st = self.mcu.mcu_com.Read_Buff()
                # print st
                # raed_str += st
                raed_str += self.mcu.mcu_com.Read_Buff()
                if self.moon_motor.StopStatus(slave):
                    raed_str += self.mcu.mcu_com.Read_Buff()
                    # self.mcu.mcu_com.close_up()
                    self.mcu.mcu_com.ClosePort()
                    break

            try:
                file_path = self.get_save_dir() + "\\" + 'roll_r.txt'
                with open(file_path, 'w') as fp:
                    fp.write(raed_str)
            except Exception,ex:
                pass

            self.mcu.r_cmdinfo.todifferenceInfo(raed_str)

            # 等待电机运动结束
            # self._wait_moo_stop([self.config_obj.Roll_slave])
            # self._stop_collect_diff()
            # time.sleep(2)
            #  进行数据处理
            file_path = self.get_save_dir() + "\\" + self.current_sn + \
                        "differnece_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"

            # test_status, msg = self.mcu.difference_data_processing(file_path)
            test_status,msg = self.mcu.difference_rawcount_processing(file_path)

            # 数据判定
            # 1. Max Touch Capacitance判定
            status1 = self._max_touch_cap()
            # 2. Touch Saturation 判定
            status2 = self._touch_Saturations()
            # 3. 触摸位置判定
            status3 = True
            # status3 = self._touch_pos()
            test_status = status1 and status2 and status3
            if test_status:
                msg = "check difference step ok"
            else:
                msg += ",check difference step fail"
            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status
        finally:
            self.current_item = 'check_difference_step'
            self._on_item_end(self.current_item, test_status, str(test_status), msg)
            self._on_display_msg('_roll_check_difference', msg, test_status)

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

    #  触摸位置判定
    def _touch_pos(self):
        test_status = True  # 是要有一个失败都是失败
        # 滚动方向不一样，触摸的起始sensor 不一样,1个是递增，1个是递减
        # limit_asc = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # limit_desc = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        limit_asc = [2, 3, 4, 5, 6, 7, 8, 9]
        limit_desc = [9, 8, 7, 6, 5, 4, 3, 2]
        touch_sensor = self.mcu.difference_cal_datas[self.mcu.Sensor_NO]
        print touch_sensor
        l0_l11 = list(set(touch_sensor))
        l0_l11.sort(key=touch_sensor.index)
        try:
            index = l0_l11.index(9)
            if index > 0:
                l0_l11 = l0_l11[index:index+8]
        except Exception:
            # 1.不存在
            pass

        # 判定
        status = False
        msg = 'fail'
        if l0_l11 == limit_asc or l0_l11 == limit_desc:
            status = True
            msg = 'touch sensor ok'
        else:
            test_status = False
            status = False
            msg = 'touch sensor fail'
        self._on_item_end("touch pos", status, str(l0_l11), msg, "x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]")
        return test_status

    # 振动测试->启动振动并采集数据
    def _vibration_check(self):
        try:
            self.current_item = 'vibration_check'
            self._on_item_start(self.current_item)
            msg = '__vibration_check fail'
            test_status = False
            self.haptics_probe.clearBuff()  # 清除缓存
            values = ''

            cnt = 2
            while cnt > 0:
                # 振动前采集数据,,持续1秒
                acc_pros = self.haptics_probe.read_angle_acc(1)
                if len(acc_pros) == 0:
                    test_status = False
                else:
                    test_status = True

                # 启动振动,采集振动数据
                test_status = self.mcu.start_Haptics()
                if test_status is False:
                    msg = self.mcu.mcu_com.message
                else:
                    # 采集振动器数据,持续2秒
                    acc_ings = self.haptics_probe.read_angle_acc(1)
                    if len(acc_ings) == 0:
                        test_status = False
                        msg = "collect acc_ing fail, no data were collected"

                    # 停止振动
                    self.mcu.stop_Haptics()
                    time.sleep(1)
                    # 等待1秒,采集振动,持续1秒
                    acc_stops = self.haptics_probe.read_angle_acc(1)
                    if len(acc_stops) == 0:
                        values += "- None,None,None"
                        test_status = False
                        msg = 'acc stop collect data fail, no data were collected'

                    # 判定数据
                    # 1. 振动前数据标准方差
                    acc_por_avg = self._cul_acc_std(acc_pros)
                    self.current_item = 'Before the vibration'
                    self._on_item_end(self.current_item, test_status, str(acc_por_avg), msg)
                    # 2. 振动数据标准方差
                    acc_ings_avg = self._cul_acc_std(acc_ings)
                    self.current_item = 'vibration'
                    test_status = acc_ings_avg[0] > acc_por_avg[0] or acc_ings_avg[1] > acc_por_avg[1] or \
                                  acc_ings_avg[2] > acc_por_avg[2]

                    if test_status is False:
                        cnt -= 1
                        continue

                    self._on_item_end(self.current_item, test_status, str(acc_ings_avg), msg)
                    # 3. 停止振动数据标准方差
                    acc_stops_avg = self._cul_acc_std(acc_stops)
                    self.current_item = 'Stop the vibration'
                    self._on_item_end(self.current_item, test_status, str(acc_stops_avg), msg)

                    # 数据合并并写入文件
                    for ls in acc_pros:
                        ls.insert(0, 'Before the vibration')
                    record_ls = acc_pros
                    # 振动前标准方差
                    ls = ["std"]
                    ls.extend(acc_por_avg)
                    record_ls.append(ls)
                    # 振动数据合并
                    for ls in acc_ings:
                        ls.insert(0, 'vibration')
                    record_ls.extend(acc_ings)
                    # 振动标准方差
                    ls = ["std"]
                    ls.extend(acc_ings_avg)
                    record_ls.append(ls)
                    # 振动停止后
                    for ls in acc_stops:
                        ls.insert(0, 'Stop the vibration')
                    record_ls.extend(acc_stops)
                    # 振动停止后标准方差
                    ls = ["std"]
                    ls.extend(acc_stops_avg)
                    record_ls.append(ls)

                    file_path = self.get_save_dir() + "\\" + self.current_sn + \
                            "_vibration_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"
                    df = pandas.DataFrame(record_ls)
                    df.columns = ["type", "x", "y", "z"]
                    df.to_csv(file_path, index=False, sep=',')
                    if test_status is True:
                        break
            return test_status
        except Exception, ex:
            cnt -= 1
            msg = 'excption:' + ex.message
            test_status = False
            return test_status
        finally:
            if self.mcu is not None:
                self.mcu.stop_Haptics()
            if isinstance(self.haptics_probe, AccelerometerBll):
                self.haptics_probe.stop_read()
            self.current_item = 'vibration_check'
            self._on_item_end(self.current_item, test_status, str(test_status), msg)
            self._on_display_msg('__vibration_check', msg, test_status)

    # 列表数据,只支持[[].[],...,[]]格式数据，并且是数字类型
    def _cul_avg(self, datas):
        df = pandas.DataFrame(datas)
        df.columns = ["x", "y", "z"]
        x_avg = df['x'].mean()
        y_avg = df['y'].mean()
        z_avg = df['z'].mean()
        return [x_avg, y_avg, z_avg]

    # 计算标准方差
    # 列表数据,只支持[[].[],...,[]]格式数据，并且是数字类型
    def _cul_acc_std(self, datas):
        if len(datas) == 0:
            return [0, 0, 0]
        else:
            df = pandas.DataFrame(datas)
            df.columns = ["x", "y", "z"]
            x_std = round(np.std(df['x']), 4)
            y_std = round(np.std(df['y']), 4)
            z_std = round(np.std(df['z']), 4)
            return [x_std, y_std, z_std]

    # 滚动测试
    def _roll_test(self, dut=True):
        return False

    # 振动测试
    def _vibration_test(self):
        return False

    # 测试结束，正常复位
    def _test_finished(self):
        return False

    # 初始化io， 默认是初始化衣服成品和半成品IO对象，子类可重写
    def _init_io(self, auto=False, port_list=None):
        try:
            msg = ''
            status = False
            try:
                # 首先检测配置是否正确，正确将不在继续检测，直接返回
                self.kmlio = KMLFATPIO(self.config_obj.IO_Port, self.config_obj.IO_baudrate)
                if self.kmlio.checkConnect():
                    status = True
                    if auto is True and port_list is not None and len(port_list) > 0:
                        port_list.remove(self.config_obj.IO_Port)
            except Exception, ex:
                msg = 'IO init exeption:' + ex.message
                status = False

            if auto and status is False:
                status, msg = self.kmlio.auto_connect(port_list)
                if status:
                    self.config_obj.IO_Port = msg
                    port_list.remove(msg)  # 成功，返回port

            if status:
                msg = 'IO ' + self.config_obj.IO_Port
                return status, msg
            else:
                status = False
                msg = 'IO init fail:' + self.kmlio.message
                return False, "IO "+self.config_obj.IO_Port
        except Exception, ex:
            status = False
            msg = 'IO init exeption:'+ex.message
            return False, "IO init exception"
        finally:
            self._on_display_msg('_init_io', msg, status)
            # self.display_msg.emit(msg, status)

    # 初始化loadcell对象
    def _loadcell(self, auto=False, port_list=None):
        try:
            msg = ''

            self.loadcell = LocalCell()
            status, msg = self.loadcell.auto_connect([self.config_obj.loadcell_port])  # 先进行配置文件参数验证
            if status is True and auto is True and port_list is not None and len(port_list) > 0:
                port_list.remove(self.config_obj.loadcell_port)

            # 配置文件端口错误，auto=True将自定检测
            if auto and status is False:
                status, msg = self.loadcell.auto_connect(port_list)
                if status:
                    self.config_obj.loadcell_port = msg
                    port_list.remove(msg)  # 成功，返回port

            if status:
                msg = 'loadcell init OK'
                return True, 'loadcell ' + self.config_obj.loadcell_port
            else:
                msg = 'loadcell init fail: ' + msg
                return False, 'loadcell '+ self.config_obj.loadcell_port
        except Exception, ex:
            status = False
            if self.loadcell is not None:
                self.loadcell.CloseSerial()
                msg = 'loadcell init exception:' + ex.message
            return False, "loadcell init exception"
        finally:
            # self.display_msg.emit(msg, init_st)
            self._on_display_msg('_loadcell', msg, status)

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

    # 电机对象初始化
    def _moon_motor(self, auto=False, port_list=None):
        try:
            msg = ''
            status = False
            self.moon_motor = MoonsController(self.config_obj.Moon_motor_Port)
            if self.moon_motor.checkConnect():
                status = True
                if auto is True and port_list is not None and len(port_list) > 0:
                    port_list.remove(self.config_obj.Moon_motor_Port)

            if auto and status is False:
                status, msg = self.moon_motor.auto_connect(port_list)
                if status:
                    self.config_obj.Moon_motor_Port = msg
                    port_list.remove(msg)  # 成功，返回port

            if status:
                msg = 'moon init OK'
            else:
                msg = 'moon init fail'
            return status, 'moon '+self.config_obj.Moon_motor_Port
        except Exception, ex:
            msg = 'moon_motor init exception' + ex.message
            status = False
            return False, 'moon_motor init exception'
        finally:
            # self.display_msg.emit(msg, status)
            self._on_display_msg('_moon_motor', msg, status)

    # 直线运动
    def _Moveline(self, slave, pos, speed, sync=True):
        return self.moon_motor.MoveLine(slave, pos, speed, ACCELEROMETER, DECELERATION, RATIO, sync=sync)

    # 等待slave_list中所有电机运动停止后在返回
    # slave_list电机地址列表
    # timeout超时时间,单位：秒，默认是30秒
    # 所有停止返回true,false返回失败
    # 返回数据(状态，未停止电机地址列表)
    def _wait_moo_stop(self, slave_list, timeout=30):
        if len(slave_list) > 0:
            endtime = time.time() + timeout
            all_stop = False
            run_list = slave_list
            while time.time() <= endtime:
                all_stop = True
                for_list = list(run_list)
                for i in range(len(for_list)):
                    if self.moon_motor.StopStatus(for_list[i]) == False:
                        all_stop = False
                    else:
                        run_list.remove(for_list[i])
                if all_stop:
                    break
        return all_stop, run_list

    # 运动停止返回true,否则返回false
    def _movestop(self, slave):
        return self.moon_motor.StopStatus(slave)

    # 蜂鸣器控制
    # timer 响和停之间的间隔,单位秒
    # count 响次数
    def _buzzer(self, count=3, timer=0.1):
        for i in range(count):
            self.kmlio.set_buzzer(0)
            time.sleep(timer)
            self.kmlio.set_buzzer(1)

    # 加速度无杆气缸电磁阀上
    def _test_finished_step1(self):
        try:
            test_status = True
            msg = ''
            status, set_data = self.kmlio.set_accelerated_up(0)
            if status is True:
                value, data = self.kmlio.get_accelerated_up(0, True)
                if value != 1:
                    test_status = False
                    msg = 'get_accelerated_up fail'
            else:
                test_status = False
                msg = 'set_accelerated_up fail'

            return test_status, msg
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status, msg
        finally:
            self._on_display_msg('_test_finished_step1', msg, test_status)

    # loadcell清零
    def _clear_loadcell(self):
        self.kmlio.set_loadcell_clear(0)
        time.sleep(0.01)
        self.kmlio.set_loadcell_clear(1)

    # 下压到指定位置，并且这个位置不会接触到dut,如果有接触，自动调整到不接触
    def _press_to_pos(self, loadcell, slave, pos, speed, timeout=30):
        # 采集loadcell数据，如果力>=minN,立即停止,判断当前力是否在min-max之间
        try:
            if isinstance(loadcell, LocalCell):
                maxN = self.config_obj.MaxN
                limitN = 0
                if maxN >= 2:
                    limitN = int(maxN/2)

                dit_pos = pos
                self._Moveline(slave, dit_pos, speed, False)

                endtime = time.time() + timeout
                no_data_cnt = 0
                loadcell.ClearBuffer()  # 执行采集前清缓存？还是每次采集清除缓存
                while time.time() <= endtime:
                    try:
                        if self._testing is False:
                            self.moon_motor.SetMoonsImmediatelyStop(slave)
                            self._on_display_msg('_press_to_pos', 'stop test', False)
                            return False

                        str_n = loadcell.ReadLocalCellSigle(timeout=0.02)
                        if str_n == 'None':
                            no_data_cnt = no_data_cnt + 1
                            time.sleep(0.01)
                        else:
                            cuurent_n = float(str_n)
                            no_data_cnt = 0
                            if cuurent_n > limitN:
                                self.moon_motor.SetMoonsImmediatelyStop(slave)
                                # datas = self.moon_motor.GetMoonsStatus(slave, 8)
                                # dit_pos = dit_pos - 500 if pos > 0 else dit_pos + 500  # 负号表示方向
                                # self._Moveline(slave, dit_pos, speed)
                                return True   # 只执行一次回退
                            else:
                                if self.moon_motor.StopStatus(slave):
                                    # 运动已经停止，且压力未大于0,保存当前pos数据
                                    # self.config_obj.Pressure_target_pos = dit_pos
                                    self.display_msg.emit('_press_to_pos to pos =:{0}'.format(dit_pos), True)
                                    return True
                        # 连续5次读不到loadcell数据(有可能loadcell掉线或坏了),退出
                        if no_data_cnt >= 5:
                            self.moon_motor.SetMoonsImmediatelyStop(slave)
                            # self.display_msg.emit('_press_to_pos fail', False)
                            self._on_display_msg('_press_to_pos', 'collect loadcell fail, no_data_cnt=5', False)
                            return False
                    except Exception, ex:
                        self._on_display_msg('_press_to_pos', 'exception:{0}'.format(ex.message), False)
            else:
                self._on_display_msg('_press_to_pos', 'loadcell object is not LocalCell type', False)
            return False
        finally:
            if isinstance(loadcell, LocalCell):
                loadcell.CloseSerial()

    # 运动到指定力位置
    # loadcell 读压力值的loadcell对象
    # slave 电机地址
    # pos 运动距离
    # speed 运动速度
    # toN 目标压力
    # deviation 目标压力误差百分比，默认是5%
    def _run_to_InitN(self, loadcell, slave, pos, speed, toN, deviation=5, timeout=30):
        # 采集loadcell数据，如果力>=minN,立即停止,判断当前力是否在min-max之间
        try:
            if isinstance(loadcell, LocalCell):
                dit_pos = pos
                minN = toN - toN * deviation / 100.00
                # maxN = toN + toN * 50 / 100.00
                maxN = toN + 0.3
                self._Moveline(slave, dit_pos, speed, False)
                endtime = time.time() + timeout
                no_data_cnt = 0
                loadcell.ClearBuffer()  # 执行采集前清缓存？还是每次采集清除缓存
                while True:
                    try:
                        if self._testing is False:
                            self.moon_motor.SetMoonsImmediatelyStop(slave)
                            self._on_display_msg('_run_to_InitN', 'stop test', False)
                            return False

                        if time.time() > endtime:
                            self.moon_motor.SetMoonsImmediatelyStop(slave)
                            return False
                        str_n = loadcell.ReadLocalCellSigle(timeout=0.01)
                        print 'str_n = {0}'.format(str_n).center(100, '-')
                        if str_n == 'None':
                            no_data_cnt = no_data_cnt + 1
                            # time.sleep(0.02)
                        else:
                            try:
                                cuurent_n = float(str_n)
                                no_data_cnt = 0
                                if cuurent_n >= MAX_N:
                                    self.moon_motor.SetMoonsImmediatelyStop(slave)
                                    str_n = loadcell.ReadLocalCellSigle(timeout=0.01)
                                    cuurent_n = float(str_n)
                                    if cuurent_n >= MAX_N:
                                        self._on_display_msg('_run_to_InitN', 'loadcell data > max_N={0}'.format(MAX_N),
                                                             False)
                                        return False
                                if cuurent_n >= minN:
                                    self.moon_motor.SetMoonsImmediatelyStop(slave)
                                    speed = 100
                                    if cuurent_n <= maxN:
                                        return True
                                    else:
                                        # 大于最大，必须回退
                                        # datas = self.moon_motor.GetMoonsStatus(slave, 8)
                                        dit_pos = dit_pos - 5000 if pos > 0 else dit_pos + 5000  # 负号表示方向
                                        self._Moveline(slave, dit_pos, speed, False)
                                else:
                                    # 已到位，必须增加运动距离，达到指定力附近
                                    # print self.moon_motor,
                                    if self.moon_motor.StopStatus(slave):
                                        dit_pos = dit_pos + 2000 if pos > 0 else dit_pos - 2000  # 负号表示方向
                                        self._Moveline(slave, dit_pos, speed, False)
                            except Exception,ex:
                                no_data_cnt = no_data_cnt + 1

                        # 连续5次读不到loadcell数据(有可能loadcell掉线或坏了),退出
                        if no_data_cnt >= 10:
                            self.moon_motor.SetMoonsImmediatelyStop(slave)
                            self._on_display_msg('_run_to_InitN', 'collect loadcell fail, no_data_cnt=5', False)
                            return False
                    except Exception, ex:
                        self.moon_motor.SetMoonsImmediatelyStop(slave)
                        self._on_display_msg('_run_to_InitN', 'exception:{0}'.format(ex.message), False)
            else:
                self._on_display_msg('_run_to_InitN', 'loadcell object is not LocalCell type', False)
            return False
        finally:
            if isinstance(loadcell, LocalCell):
                loadcell.CloseSerial()

    # 调试使用
    # 滚动压力实验
    # 参数：执行次数
    def roll_press_test(self, count=50):
        import datetime
        from Comm.CSVHelper import CSVHelper
        head = "滚动脉冲,开始前压力,接触压力,滚动压力,复位后压力"
        csv_obj = CSVHelper(r".\\" + datetime.datetime.now().strftime("%Y%m%d")+'.csv', head)
        for i in range(count):
            try:
                print 'count = {0}'.format(i).center(100, '-')
                str_n = '100000'+','
                msg = '__roll_test_step2 ok'
                slave = self.config_obj.Push_down_slave
                pos1 = self.config_obj.Pressure_target_pos
                pos = self.config_obj.Roll_pressure_pos
                maxN = 0.92
                # 开始前压力
                str_n = str_n + self.loadcell.ReadLocalCellSigle(timeout=0.02)+','
                # 检测之前清除loadcell压力表数据
                self._clear_loadcell()
                # 运动到目标1pos
                test_status = self._press_to_pos(self.loadcell, slave, pos1, SPEED)
                if test_status is False:
                    msg = 'roll_test_step2 run target pos1 fail'
                    self.display_msg.emit(msg, False)

                # 开始运动并检测压力范围
                if test_status:
                    # 检测之前清除loadcell压力表数据
                    # self._clear_loadcell()
                    test_status = self._run_to_InitN(self.loadcell, slave, pos, 50, maxN)
                    if test_status is False:
                        msg = 'roll_test_step2 touch fail'
                    else:
                        time.sleep(2)           #
                        # 滚动前压力-->接触压力
                        str_n = str_n + self.loadcell.ReadLocalCellSigle(timeout=0.02)+','
                        roll_slave = self.config_obj.Roll_slave
                        test_status = self._Moveline(roll_slave, 100000, ROLL_SPEED, False)         # 开始滚动
                        if test_status:
                            while True:
                                # 滚动过程压力变化
                                str_n = str_n + ' ' + self.loadcell.ReadLocalCellSigle(timeout=0.01)
                                if self.moon_motor.StopStatus(roll_slave):
                                    # 下压复位
                                    self._Moveline(slave, 0, SPEED)
                                    self._Moveline(roll_slave, 0, SPEED)
                                    # 复位完成后读压力表数据
                                    str_n = str_n + ',' + self.loadcell.ReadLocalCellSigle(timeout=0.01)
                                    # 写入数据
                                    csv_obj.write(str_n)
                                    break
            except Exception, ex:

                test_status = False
                msg = '__roll_test_step2 exception:' + ex.message
                return test_status
            finally:
                self.display_msg.emit(msg, test_status)

    # 调试使用
    # 振动实验
    # 参数:执行次数
    def acc_test(self, count=20):
        from PyQt4 import QtGui
        import datetime
        from Comm.CSVHelper import CSVHelper
        head = "实验次数,X加速度,Y加速度,Z加速度,X角速度,Y角速度,Z角速度,X角度,Y角度, Z角度"
        csv_obj = CSVHelper(r".\\acc" + datetime.datetime.now().strftime("%Y%m%d") + '.csv', head)
        str_value = ''

        for i in range(count):
            try:
                test_list = []
                # acc_pro = str(i) + ','
                print 'count={0}'.format(i).center(100, '-')
                # 下
                status, set_data = self.kmlio.set_accelerated_down(False)
                time.sleep(5)
                if status is True:
                    # value, data = self.kmlio.get_accelerated_down(0, True)
                    value = 1
                    if value != 1:
                        test_status = False
                        msg = 'get_accelerated_down 1 solenoid valve fail'
                    else:
                        # time.sleep(1)
                        # acc_info = self.haptics_probe.read_data()
                        # acc_pro += acc_info.tostring() + ',\n'
                        # test_list.append(acc_pro)
                        # QtGui.QMessageBox.question(None, u'提示', '请打开手机振动,打开后按下按键', QtGui.QMessageBox.Yes)
                        # print '请打开手机振动, 打开后按任意键继续...'
                        # raw_input()
                        # print '继续测试'
                        time.sleep(1)
                        st = time.time()
                        while time.time() - st <= 1:
                            acc_info = self.haptics_probe.read_data()
                            str_value = str(i) + 'pro,' + acc_info.tostring() + '\n'
                            test_list.append(str_value)
                        self.haptics_probe.close_serial()
                        time.sleep(1)
                        self.mcu.start_Haptics()
                        # 振动开始，采集振动数据，时常10秒
                        st = time.time()
                        while time.time() - st <= 10:
                            acc_info = self.haptics_probe.read_data()
                            if acc_info is not None:
                                str_value = str(i) + ',' + acc_info.tostring() + '\n'
                                test_list.append(str_value)
                                str_value = ''
                        self.haptics_probe.close_serial()
                        time.sleep(1)
                        self.mcu.stop_Haptics()
                        time.sleep(1)
                        st = time.time()
                        while time.time() - st <= 1:
                            acc_info = self.haptics_probe.read_data()
                            if acc_info is not None:
                                str_value = str(i) + 'end,' + acc_info.tostring() + '\n'
                                test_list.append(str_value)
                                str_value = ''
                        self.haptics_probe.close_serial()
                        # 复位--上
                        status, set_data = self.kmlio.set_accelerated_up(0)
                        if status is True:
                            value, data = self.kmlio.get_accelerated_up(0, True)
                            if value != 1:
                                str_value += ','
                                test_status = False
                                msg = 'get_accelerated_up 1 solenoid valve fail'
                            else:
                                time.sleep(1)
                        # str_value += '10秒'
                        csv_obj.writeLines(test_list)
                        time.sleep(10)
            except Exception,ex:
                print ex.message
                self.mcu.start_Haptics()


if __name__ == "__main__":
    appconfig = APPConfigparse.APPConfigparse(r'../config.ini')
    obj = KML_tester_base(appconfig, None)
    init_st = obj.check_connect(auto=False, port_list=["COM6"])
    for i in range(0, len(init_st)):
        print init_st[i]

    # obj.roll_press_test()
    obj.acc_test()