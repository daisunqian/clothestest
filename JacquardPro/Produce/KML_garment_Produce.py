# -*- coding=utf-8 -*-

# from PyQt4.QtCore import pyqtSignal, QObject
# from PyQt4 import QtGui
import time
from Produce.IProduce import IProduce
from FixtureControl.KML_garment_tester import KML_garment_tester
from FixtureControl.APPConfigparse import APPConfigparse
from Controller import KMLFATPIO, MCUComm
from Comm import MoonsController, Accelerometer, LoadCellData


class KML_garment_Produce(IProduce):

    def __init__(self, appconfig):
        super(KML_garment_Produce, self).__init__(appconfig)
        self.jacquard_tester = KML_garment_tester(self.appconfig, None)
        self.jacquard_tester.check_connect(True, self._get_ports())

    # 开始执行测试
    def start_check(self):
        if self._init():
            self._input_io_check()
            self._output_io_check()
            self._moon_check()
            self._loadcell_check()
            self._acc_check()
            self._mcu_check()

    # 初始化
    def _init(self):
        try:
            if isinstance(self.appconfig, APPConfigparse):
                if self.jacquard_tester is None:
                    print ("test object init fail, test type {0}".format(self.appconfig.Test_type))
                else:
                    self.jacquard_tester.display_msg.connect(self._on_display_msg)
                    port_list = self._get_ports()
                    init_st = self.jacquard_tester.check_connect(auto=True, port_list=port_list)
                    status = self.jacquard_tester.backhome()
                    if status:
                        self._on_display_msg(u'正在进行电机home校准...', True)
                        self.jacquard_tester.moon_motor.SetMoonsHome(self.appconfig.Push_down_subordinate)
                        self.jacquard_tester.moon_motor.SetMoonsHome(self.appconfig.Roll_subordinate)
                        self._on_display_msg(u'电机home校准完成', True)
                        return True
            else:
                self._on_display_msg(u'配置对象不是' + 'APPConfigparse' + u"类型", False)
                return False
        except Exception, ex:
            self._on_display_msg('_init exception:' + ex.message, False)
            return False

    # 输入IO检测
    def _input_io_check(self):
        try:
            if self.jacquard_tester is not None:
                if isinstance(self.jacquard_tester.kmlio, KMLFATPIO.KMLFATPIO):
                    intput_io_limit = KMLFATPIO.INPUT_IO_LIMIT
                    # in1
                    in_index = 1

                    self._in_io_check(u'急停按钮', intput_io_limit[in_index-1],
                                      self.jacquard_tester.kmlio.get_E_Stop)
                    # in2
                    in_index = 2
                    self._in_io_check(u'左边star按钮', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_start_button1)
                    # in3
                    in_index = 3
                    self._in_io_check(u'右边star按钮', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_start_button2)
                    # in4
                    in_index = 4
                    self._in_io_check(u'reset按钮', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_reset_button)
                    # in5
                    in_index = 5
                    self._in_io_check(u'加速度无杆气缸上位', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_accelerated_up)
                    # in6
                    in_index = 6
                    self._in_io_check(u'加速度无杆气缸下位', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_accelerated_down)
                    # in7
                    in_index = 7
                    self._in_io_check(u'张紧气缸拉紧', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_stretch_tensioning)
                    # in8
                    in_index = 8
                    self._in_io_check(u'张紧气缸放松', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_stretch_relax)
                    # in9
                    in_index = 9
                    self._in_io_check(u'夹爪气缸夹紧', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_claw_clamp)
                    # in10
                    in_index = 10
                    self._in_io_check(u'夹爪气缸松开', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_claw_loosen)
                    # in11
                    in_index = 11
                    self._in_io_check(u'滚压驱动器报警', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_roll_warning)
                    # in12
                    in_index = 12
                    self._in_io_check(u'get_loadcell_warning', intput_io_limit[in_index - 1],
                                      self.jacquard_tester.kmlio.get_loadcell_warning)
                else:
                    self._ontest_step_finished(u'无法测试', 'IO object not init', "IO object not init", False,
                                   "IO" + u'I对象错误，无法检测' + "IO")
            else:
                self._ontest_step_finished(u'输入IO无法检测', 'object not init', "object not init", False, u'测试对象未创建错误，无法检测')
        except Exception, ex:
            self._ontest_step_finished(u'输入IO检测异常', 'exception', "exception", False, u'异常，无法检测 : ' + ex.message)

    # 输入io检测
    def _output_io_check(self):
        try:
            if self.jacquard_tester is not None:
                if isinstance(self.jacquard_tester.kmlio, KMLFATPIO.KMLFATPIO):
                    # out1
                    self._on_test_step_start(u'两边start按键led')
                    self.jacquard_tester.kmlio.set_start_lamp(0)
                    time.sleep(1)
                    status = self._on_messag_box_open(u'询问', u'两边start按键Led灯是否点亮?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'两边start按键Led灯是否点亮?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    self._ontest_step_finished(u'两边start按键led', u'点亮', u'点亮' if status else u'未点亮', status,
                                   u'点亮' if status else u'未点亮')
                    # out2
                    self._on_test_step_start(u'reset按键led')
                    self.jacquard_tester.kmlio.set_reset_lamp(0)
                    time.sleep(1)
                    status = self._on_messag_box_open(u'询问', u'reset按键Led灯是否点亮?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'reset按键Led灯是否点亮?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    self._ontest_step_finished(u'reset按键led', u'点亮', u'点亮' if status else u'未点亮', status,
                                   u'点亮' if status else u'未点亮')
                    # out3
                    self._on_test_step_start(u'绿灯点亮')
                    self.jacquard_tester.kmlio.set_red(1)
                    self.jacquard_tester.kmlio.set_blue(1)
                    self.jacquard_tester.kmlio.set_green(0)
                    time.sleep(1)
                    status = self._on_messag_box_open(u'询问', u'绿灯是否点亮?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'绿灯是否点亮?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    self._ontest_step_finished(u'绿灯点亮', u'点亮', u'点亮' if status else u'未点亮', status,
                                   u'点亮' if status else u'未点亮')
                    # out4
                    self._on_test_step_start(u'红灯点亮')
                    self.jacquard_tester.kmlio.set_red(0)
                    self.jacquard_tester.kmlio.set_blue(1)
                    self.jacquard_tester.kmlio.set_green(1)
                    time.sleep(1)
                    status = self._on_messag_box_open(u'询问', u'红灯是否点亮?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'红灯是否点亮?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    self._ontest_step_finished(u'红灯点亮', u'点亮', u'点亮' if status else u'未点亮', status,
                                   u'点亮' if status else u'未点亮')
                    # out5
                    self._on_test_step_start(u'蓝灯点亮')
                    self.jacquard_tester.kmlio.set_red(1)
                    self.jacquard_tester.kmlio.set_blue(0)
                    self.jacquard_tester.kmlio.set_green(1)
                    time.sleep(1)
                    status = self._on_messag_box_open(u'询问', u'蓝灯是否点亮?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'蓝灯是否点亮?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    self._ontest_step_finished(u'蓝灯点亮', u'点亮', u'点亮' if status else u'未点亮', status,
                                   u'点亮' if status else u'未点亮')
                    # out6
                    self._on_test_step_start(u'蜂鸣器')
                    self.jacquard_tester.kmlio.set_buzzer(0)
                    time.sleep(1)
                    self.jacquard_tester.kmlio.set_buzzer(1)
                    status = self._on_messag_box_open(u'询问', u'蜂鸣器是否鸣叫?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'蜂鸣器是否鸣叫?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    self._ontest_step_finished(u'蜂鸣器', u'鸣叫', u'鸣叫' if status else u'未鸣叫', status,
                                   u'鸣叫' if status else u'未鸣叫')
                    # out7
                    self._on_test_step_start(u'加速度无杆气缸电磁阀下')
                    self.jacquard_tester.kmlio.set_accelerated_down(0)
                    self.jacquard_tester.kmlio.set_accelerated_up(1)
                    time.sleep(1)
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'加速度无杆气缸电磁阀下?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    status = self._on_messag_box_open(u'询问', u'加速度无杆气缸电磁阀下?')
                    if status:
                        # 检测输入io
                        value, data = self.jacquard_tester.kmlio.get_accelerated_down()
                        status = value == 1
                    self._ontest_step_finished(u'加速度无杆气缸电磁阀下', u'下', u'下' if status else u'上', status,
                                   u'下' if status else u'上')
                    # out8
                    self._on_test_step_start(u'加速度无杆气缸电磁阀上')
                    self.jacquard_tester.kmlio.set_accelerated_up(0)
                    self.jacquard_tester.kmlio.set_accelerated_down(1)
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'加速度无杆气缸电磁阀上?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    status = self._on_messag_box_open(u'询问', u'加速度无杆气缸电磁阀上?')
                    if status:
                        # 检测输入io
                        value, data = self.jacquard_tester.kmlio.get_accelerated_up()
                        status = value == 1
                    self._ontest_step_finished(u'加速度无杆气缸电磁阀上', u'上', u'上' if status else u'下', status,
                                   u'上' if status else u'下')
                    # out9--张紧
                    self._on_test_step_start(u'气缸张紧')
                    self.jacquard_tester.kmlio.set_stretch_tensioning(0)
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'气缸是否张紧?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    status = self._on_messag_box_open(u'询问', u'气缸张紧?')
                    if status:
                        # 检测输入io
                        value, data = self.jacquard_tester.kmlio.get_stretch_tensioning()
                        status = value == 1

                    self._ontest_step_finished(u'气缸张紧', u'张紧', u'张紧' if status else u'未张紧', status,
                                   u'张紧' if status else u'未张紧,请检查感应器和气压')
                    # out9--放松
                    self._on_test_step_start(u'张紧气缸放松')
                    self.jacquard_tester.kmlio.set_stretch_tensioning(1)
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'气缸是否放松?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    status = self._on_messag_box_open(u'询问', u'张紧气缸放松?')
                    if status:
                        # 检测输入io
                        value, data = self.jacquard_tester.kmlio.get_stretch_relax()
                        status = value == 1

                    self._ontest_step_finished(u'张紧气缸放松', u'放松', u'放松' if status else u'未放松', status,
                                   u'放松' if status else u'未放松,请检查感应器和气压')
                    # out10--爪紧
                    self._on_test_step_start(u'夹爪气缸')
                    self.jacquard_tester.kmlio.set_stretch_relax(0)
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'夹爪气缸是否抓紧?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    status = self._on_messag_box_open(u'询问', u'夹爪气缸?')
                    if status:
                        # 检测输入io
                        value, data = self.jacquard_tester.kmlio.get_claw_clamp()
                        status = value == 1

                    self._ontest_step_finished(u'夹爪气缸', u'夹爪', u'夹爪' if status else u'未夹爪', status,
                                   u'夹爪' if status else u'未夹爪')
                    # out10--放松
                    self._on_test_step_start(u'夹爪气缸松开')
                    self.jacquard_tester.kmlio.set_stretch_relax(1)
                    status = self._on_messag_box_open(u'询问', u'夹爪气缸是否松开?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'夹爪气缸是否松开?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if status:
                        # 检测输入io
                        value, data = self.jacquard_tester.kmlio.get_claw_loosen()
                        status = value == 1

                    self._ontest_step_finished(u'夹爪气缸松开', u'松开', u'松开' if status else u'未松开', status,
                                   u'松开' if status else u'未松开')
                    # out11
                    self._on_test_step_start(u'真空阀开关')
                    self.jacquard_tester.kmlio.set_vacuum_switch(0)
                    time.sleep(1)
                    self.jacquard_tester.kmlio.set_vacuum_switch(1)
                    status = self._on_messag_box_open(u'询问', u'真空阀开关是否开?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'真空阀开关是否开?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if status:
                        # 检测输入io
                        value, data = self.jacquard_tester.kmlio.get_vacuo()
                        status = value == 0

                    self._ontest_step_finished(u'真空阀开关', u'上', u'开' if status else u'未开', status,
                                   u'开' if status else u'未开')
                else:
                    self._ontest_step_finished(u'输出IO无法检测', 'IO object not init', "IO object not init", False,
                                   "IO" + u'I对象错误，无法检测' + "IO")

            else:
                self._ontest_step_finished(u'输出IO无法检测', 'object not init', "object not init", False, u'测试对象未创建错误，无法检测')
        except Exception, ex:
            self._ontest_step_finished(u'输出IO检测异常', 'exception', "exception", False, u'异常，无法检测 : ' + ex.message)

    # 电机检测
    def _moon_check(self):
        try:
            if self.jacquard_tester is not None:
                if isinstance(self.jacquard_tester.moon_motor, MoonsController.MoonsController):
                    # 滚动电机运动到指定位置
                    self._on_test_step_start(u'滚动电机运动')
                    status = self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Roll_subordinate,
                                                                      self.appconfig.Roll_start_pos, 600, 300, 300)

                    # rst = QtGui.QMessageBox.question(None, u'询问', u'是否到位?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    status = self._on_messag_box_open(u'询问', u'滚动电机运动是否到位?')
                    self._ontest_step_finished(u'滚动电机运动', u'到位', u'到位' if status else u'未到位', status,
                                               u'到位' if status else u'未到位')
                    # 滚动电机复位
                    self._on_test_step_start(u'滚动电机复位')
                    status = self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Roll_subordinate,0, 600, 300, 300)
                    status = self._on_messag_box_open(u'询问', u'滚动电机复位是否到位?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'是否到位?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    self._ontest_step_finished(u'滚动电机复位', u'到位', u'到位' if status else u'未到位', status,
                                               u'到位' if status else u'未到位')
                    # 下压电机运动到Pressure_target_pos位置
                    self._on_test_step_start(u'下压电机运动')
                    status = self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Push_down_subordinate,
                                                                      self.appconfig.Pressure_target_pos,
                                                                      600, 300, 300)
                    status = self._on_messag_box_open(u'询问', u'下压电机运动是否到位?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'是否到位?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    self._ontest_step_finished(u'下压电机运动', u'到位', u'到位' if status else u'未到位', status,
                                               u'到位' if status else u'未到位')

                    # 下压电机运动复位
                    self._on_test_step_start(u'下压电机运动复位')
                    status = self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Push_down_subordinate, 0, 600, 300, 300)
                    status = self._on_messag_box_open(u'询问', u'下压电机运动复位是否到位?')
                    # rst = QtGui.QMessageBox.question(None, u'询问', u'是否到位?',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    # status = rst == QtGui.QMessageBox.Yes
                    self._ontest_step_finished(u'下压电机运动复位', u'到位', u'到位' if status else u'未到位', status,
                                               u'到位' if status else u'未到位')
                else:
                    self._ontest_step_finished(u'电机运动', u'到位', u'未到位', False, u'电机对象不是MoonsControllerl类型')
            else:
                self._ontest_step_finished(u'电机运动无法检测', 'object not init', "object not init",
                                           False, u'测试对象未创建错误，无法检测')
        except Exception, ex:
            self._ontest_step_finished(u'电机运动无法检测', 'exception', "exception", False,
                                       u'无法检测 : ' + ex.message)

    # loadcell check
    def _loadcell_check(self):
        try:
            if self.jacquard_tester is not None:
                if isinstance(self.jacquard_tester.loadcell, LoadCellData.LocalCell):
                    # 滚动电机运动到指定位置
                    self._on_test_step_start(u'loadcell检测')
                    status = self._on_messag_box_open(u'询问', u'请在30内顶上滚动器，使压力表有压力数据，按下yes键后开始计时')
                    # rst = QtGui.QMessageBox.question(None, u'询问',
                    #                                  u'请在30内顶上滚动器，使压力表有压力数据，按下yes键后开始计时',
                    #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if status:
                        st_time = time.time()
                        status = False
                        while time.time() - st_time <= 30:
                            load_data = self.jacquard_tester.loadcell.ReadLocalCellSigle(timeout=1)
                            if load_data is not None:
                                try:
                                    f_d = float(load_data)
                                    if f_d > 0:
                                        status = True
                                        self._ontest_step_finished(u'loadcell检测', u'采集', load_data, True, u'检测成功')
                                        break
                                    else:
                                        continue
                                except Exception, ex1:
                                    continue
                        if status is False:
                                self._ontest_step_finished(u'loadcell检测', u'采集', u'检测失败', False,
                                                           u'采集失败,请检测线路')
                    else:
                        self._ontest_step_finished(u'loadcell检测', u'采集', u'检测失败', False,
                                                   u'采集失败,未进行检测')
                else:
                    self._ontest_step_finished(u'loadcell检测', u'错误', u'错误', False, u'acc对象不是AccelerometerBll类型')
            else:
                self._ontest_step_finished(u'loadcell检测', 'object not init', "object not init",
                                           False, u'测试对象未创建错误，无法检测')
        except Exception, ex:
            self._ontest_step_finished(u'loadcell检测', 'exception', "exception", False,
                                       u'无法检测 : ' + ex.message)

    # 振动器检测
    def _acc_check(self):
        try:
            if self.jacquard_tester is not None:
                if isinstance(self.jacquard_tester.haptics_probe, Accelerometer.AccelerometerBll):
                    # 滚动电机运动到指定位置
                    self._on_test_step_start(u'振动器检测')
                    acc_info = self.jacquard_tester.haptics_probe.read_data(timeout=20)
                    if acc_info is not None:
                        self._ontest_step_finished(u'振动器检测', u'采集', acc_info.tostring(), True,
                                                   u'采集失败,请检测线路')
                    else:
                        self._ontest_step_finished(u'振动器检测', u'采集', u'采集失败', False,
                                                   u'采集失败,请检测线路')
                else:
                    self._ontest_step_finished(u'振动器无法检测', u'错误', u'错误', False, u'acc对象不是AccelerometerBll类型')
            else:
                self._ontest_step_finished(u'振动器无法检测', 'object not init', "object not init",
                                           False, u'测试对象未创建错误，无法检测')
        except Exception, ex:
            self._ontest_step_finished(u'振动器无法检测', 'exception', "exception", False,
                                       u'无法检测 : ' + ex.message)

    # mcu检测
    def _mcu_check(self):
        try:
            if self.jacquard_tester is not None:
                if isinstance(self.jacquard_tester.mcu, MCUComm.MCUComm):
                    # 滚动电机运动到指定位置
                    self._on_test_step_start(u'MCU检测')
                    # acc_info = self.jacquard_tester.mcu.read_data(timeout=20)
                    # if acc_info is not None:
                    #     self._ontest_step_finished(u'MCU检测', u'采集', acc_info.tostring(), True,
                    #                                u'采集失败,请检测线路')
                    # else:
                    #     self._ontest_step_finished(u'MCU检测', u'采集', u'采集失败', False,
                    #                                u'采集失败,请检测线路')
                    self._ontest_step_finished(u'MCU无法检测', u'错误', u'错误', False, u'未实现mcu功能')
                else:
                    self._ontest_step_finished(u'MCU无法检测', u'错误', u'错误', False, u'acc对象不是MCUComm类型')
            else:
                self._ontest_step_finished(u'MCU无法检测', 'object not init', "object not init",
                                           False, u'测试对象未创建错误，无法检测')
        except Exception, ex:
            self._ontest_step_finished(u'振动器无法检测', 'exception', "exception", False,
                                       u'无法检测 : ' + ex.message)

    # input io check
    def _in_io_check(self, name, limitvalue, funcation):
        try:
            self._on_test_step_start(name)
            value, data = funcation()
            status = value == limitvalue
            msg = name + u'正常' if status else u'错误'
        except Exception, ex:
            status = False
            msg = name + u'检测异常：' + ex.message
        # try:
        #     str_limit = str(limitvalue)
        # except Exception, ex:
        #     str_limit = limitvalue
        self._ontest_step_finished(name, str(limitvalue), str(value), status, msg)