# -*- coding:utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui, Qt
# from PyQt4.QtGui import QBrush, QColor
from PyQt4.QtCore import QTimer
from ui_demo.garment_testui import Ui_MainWindow
import serial.tools.list_ports
import datetime
from FixtureControl.APPConfigparse import APPConfigparse
from FixtureControl.Limit import LimitConfig
from FixtureControl.JacpuardTestFactory import JacpuardTestFactory
# from ui_demo.loadcellcollect import loadcellcollect
from FixtureControl import KML_tester_base
from threading import Thread
from ui_demo import garment_testui
import time
import serial


GRAY_backgroud = "background-color:rgb(192, 192, 192)"
YELLOW_background = "background-color:rgb(255,255,0)"
RED_background = "background-color:rgb(255,0,0)"
GREEN_background = "background-color:rgb(0,255,0)"


class Garment_MainWindow(Ui_MainWindow):
    appendInfo = QtCore.pyqtSignal(str, int)               # 修改信息
    changebackgoundEvent = QtCore.pyqtSignal(QWidget, str)
    changedcheckedEvent = QtCore.pyqtSignal(QCheckBox, bool)   # 改变qcheckbox选择状态
    stoptimerEvent = QtCore.pyqtSignal()                # 停止定时器信号
    changedEvent = QtCore.pyqtSignal()                  # 更新结束信号

    def __init__(self):
        super(Garment_MainWindow, self).__init__()
        # io 定时器
        self.io_timer = QTimer()
        self.io_timer.timeout.connect(self._IO_timer)
        # 自定义信号连接
        self.appendInfo.connect(self.__appendInfo)
        self.changebackgoundEvent.connect(self.__changebackgound)
        self.changedcheckedEvent.connect(self.__changedchecked)
        self.changedEvent.connect(self.__changedEvent)
        self.stoptimerEvent.connect(self._stop_io_timer)
        # 初始化配置文件对象
        self.appconfig = APPConfigparse(r'./config.ini')
        self.limitConfig = LimitConfig(r'./limit.ini')
        self.__appText("config init success")
        # 初始化UI 数据
        self.init_statusbar()
        self._init_port()
        self._init_button_event()
        self._init_ui_data()
        # 对象初始化
        self.jacquard_tester = JacpuardTestFactory.create_JacpuardTest(self.appconfig.Test_type,
                                                                       self.appconfig, self.limitConfig)
        if self.jacquard_tester is None:
            self.__appText("test object init fail, test type {0}".format(self.appconfig.Test_type))
        else:
            self.jacquard_tester.display_msg.connect(self.__display_msg)
            self.jacquard_tester.connected_finished.connect(self.__obj_connected)
            port_list = self._get_ports()
            self.__appText(str(port_list))
            init_st = self.jacquard_tester.check_connect(auto=True, port_list=port_list)
            # 每次软件启动找一次home
        self._reading_loadcell = False     # True正在采集loadcell数据
        self._reading_acc = False          # True正在采集振动器数据
        self._current_step = 0             # 当前测试步骤
        self._testing = False              # 正在测试状态,true
        self._test_count = 0               # 测试次数
        # 软件启动时找home以及复位
        start_th = Thread(target=self._start_reset)
        start_th.start()

        # 启动定时器
        self._start_io_timer()

    # 软件启动时找home以及复位
    def _start_reset(self):
        #   启动时,执行一次复位操作
        self.__appText(u'正在复位...')
        status = self._reset()
        self.__appText(u'复位完成'if status else u'复位失败')
        # if status and self.jacquard_tester.moon_motor:
        #     self.__appText(u'正在进行电机home校准...')
        #     self.jacquard_tester.moon_motor.SetMoonsHome(self.appconfig.Push_down_subordinate)
        #     self.jacquard_tester.moon_motor.SetMoonsHome(self.appconfig.Roll_subordinate)
        #     self.__appText(u'电机home校准完成')

    # 端口初始化完成信号处理
    def __obj_connected(self, init_infos):
        self.__set_statusbar(init_infos)

    # 信息
    def __display_msg(self, msg, status):
        self.__appText(msg, 1 if status is True else 2)

    # 获取pc所有可用端口
    def _get_ports(self):
        port_list = []
        ports_obj = serial.tools.list_ports.comports()
        for port_obj in ports_obj:
            port_list.append(list(port_obj)[0])
        return port_list

    # 初始化端口
    def _init_port(self):
        port_list = list(serial.tools.list_ports.comports())
        for port_obj in port_list:
            self.comboBox_5.addItem(port_obj.device)
            self.comboBox.addItem(port_obj.device)
            self.comboBox_6.addItem(port_obj.device)
            self.comboBox_4.addItem(port_obj.device)
            self.comboBox_2.addItem(port_obj.device)

        index = self.comboBox_5.findText(self.appconfig.Moon_motor_Port)
        if index >= 0:
            self.comboBox_5.setCurrentIndex(index)
        else:
            self.comboBox_5.setCurrentIndex(-1)

        index = self.comboBox.findText(self.appconfig.loadcell_port)
        if index >= 0:
            self.comboBox.setCurrentIndex(index)
        else:
            self.comboBox.setCurrentIndex(-1)

        index = self.comboBox_6.findText(self.appconfig.Acc_port)
        if index >= 0:
            self.comboBox_6.setCurrentIndex(index)
        else:
            self.comboBox_6.setCurrentIndex(-1)

        index = self.comboBox_2.findText(self.appconfig.MCU_Port)
        if index >= 0:
            self.comboBox_2.setCurrentIndex(index)
        else:
            self.comboBox_2.setCurrentIndex(-1)

        index = self.comboBox_4.findText(self.appconfig.IO_Port)
        if index >= 0:
            self.comboBox_4.setCurrentIndex(index)
        else:
            self.comboBox_4.setCurrentIndex(-1)

        self.__appText('port loaded')

    # 状态栏初始化
    def init_statusbar(self):
        # *********相邻Label设置固定的间隔？？？
        # self.label1.setAcceptDrops(True)
        # 创建label
        self.label1_status = QLabel()
        self.label2_status = QLabel()
        self.label3_status = QLabel()
        self.label4_status = QLabel()
        self.label5_status = QLabel()
        self.label6_status = QLabel()
        self.label7_status = QLabel()
        self.label8_status = QLabel()

        # 设置label的最小的宽度,为达到平铺设置为150，最小宽度可重设
        self.label1_status.setMinimumWidth(150)
        self.label2_status.setMinimumWidth(150)
        self.label3_status.setMinimumWidth(150)
        self.label4_status.setMinimumWidth(150)
        self.label5_status.setMinimumWidth(150)
        self.label6_status.setMinimumWidth(150)
        self.label7_status.setMinimumWidth(150)
        self.label8_status.setMinimumWidth(150)

        # 显示label中的内容至状态栏中
        self.statusbar.addWidget(self.label1_status)
        self.statusbar.addWidget(self.label2_status)
        self.statusbar.addWidget(self.label3_status)
        self.statusbar.addWidget(self.label4_status)
        self.statusbar.addWidget(self.label5_status)
        self.statusbar.addWidget(self.label6_status)
        self.statusbar.addWidget(self.label7_status)
        self.statusbar.addWidget(self.label8_status)

    # 初始化信息显示到状态栏
    def __set_statusbar(self, init_st):
        self.label1_status.setText(init_st[0][1])
        if init_st[0][0]:
            self.label1_status.setStyleSheet(GREEN_background)
        else:
            self.label1_status.setStyleSheet(RED_background)

        self.label2_status.setText(init_st[1][1])
        if init_st[1][0]:
            self.label2_status.setStyleSheet(GREEN_background)
        else:
            self.label2_status.setStyleSheet(RED_background)

        self.label3_status.setText(init_st[2][1])
        if init_st[2][0]:
            self.label3_status.setStyleSheet(GREEN_background)
        else:
            self.label3_status.setStyleSheet(RED_background)

        self.label4_status.setText(init_st[3][1])
        if init_st[3][0]:
            self.label4_status.setStyleSheet(GREEN_background)
        else:
            self.label4_status.setStyleSheet(RED_background)

        self.label5_status.setText(init_st[4][1])
        if init_st[4][0]:
            self.label5_status.setStyleSheet(GREEN_background)
        else:
            self.label5_status.setStyleSheet(RED_background)

        # self.label6_status.setText(init_st[5][1])
        # if init_st[5][0]:
        #     self.label6_status.setStyleSheet(GREEN_background)
        # else:
        #     self.label6_status.setStyleSheet(RED_background)
        #
        # self.label6_status.setText(init_st[6][1])
        # if init_st[6][0]:
        #     self.label6_status.setStyleSheet(GREEN_background)
        # else:
        #     self.label6_status.setStyleSheet(RED_background)

    # 初始化按键点击信号
    def _init_button_event(self):
        self.pushButton_3.clicked.connect(self._roll_start_pos)      # 滚动开始位置
        self.pushButton_6.clicked.connect(self._roll_down_run)       # 滚压下压
        # self.pushButton_12.clicked.connect(self._roll_down_reset)  # 滚压下压复位
        self.pushButton_8.clicked.connect(self._roll_run)             # 滚动运动(前后运动)
        self.pushButton_7.clicked.connect(self._acc_run)              # 振动器电机移动
        self.pushButton_11.clicked.connect(self._roll_reset)          # 滚动运动复位
        self.pushButton_10.clicked.connect(self._roll_down_reset)     # 下压电机复位(上下运动)
        self.btn_press_home.clicked.connect(self._moon_press_home)    # 下压电机回home
        self.btn_roll_home.clicked.connect(self._moon_roll_home)      # 滚动电机回home
        self.pushButton_2.clicked.connect(self._mcu_collect)          # MCU采集
        self.pushButton.clicked.connect(self._rectangle_loadcell)     # loadcell采集
        self.pushButton_28.clicked.connect(self._accelerometer)       # 加速振动器数据采集
        self.btn_save.clicked.connect(self._save_config)           # 保存参数到配置文件
        self.chk_out1.clicked.connect(self._start_lamp)           # 启动指示灯
        self.chk_out2.clicked.connect(self._reset_lamp)          # 启动指示灯
        self.chk_out3.clicked.connect(self._green_lamp)          # 三色指示灯绿色
        self.chk_out4.clicked.connect(self._red_lamp)            # 三色指示灯红色
        self.chk_out5.clicked.connect(self._blue_lamp)           # 三色指示灯蓝色
        self.chk_out6.clicked.connect(self._buzzer)              # 蜂鸣器
        self.chk_out7.clicked.connect(self._acc_cylinder_up)     # 加速度无杆气缸电磁阀上
        self.chk_out8.clicked.connect(self._acc_cylinder_down)   # 加速度无杆气缸电磁阀下
        self.chk_out9.clicked.connect(self._stretch_cylinder)    # 张紧气缸
        self.chk_out10.clicked.connect(self._clamp_cylinder)     # 夹爪气缸
        self.chk_out11.clicked.connect(self._vacuum_switch)      # 真空阀开关
        self.chk_out12.clicked.connect(self._clear_loadcell)     # loadcell清零
        self.btn_fix_check.clicked.connect(self._fix_check)               # 治具检测
        self.btn_roll_test.clicked.connect(self._roll_test)               # 滚压测试
        self.btn_acc_test.clicked.connect(self._acc_test)                 # 振动测试
        self.btn_test_finished.clicked.connect(self._test_finished)       # 测试结束
        self.btn_auto_test.clicked.connect(self._auto_test)               # 自动测试
        self.btn_loop_test.clicked.connect(self._loop_test)               # 自动测试
        self.btn_reset.clicked.connect(self._reset)                       # 复位
        self.__appText('ui button clicked singnal init finished')

    # 初始化UI控件数据
    def _init_ui_data(self):
        self.lineEdit.setText(str(self.appconfig.Roll_start_pos))                    # 滚动测试起始位置
        self.lineEdit_9.setText(str(self.appconfig.Push_down_subordinate))                 # 下压电机地址
        self.lineEdit_10.setText(str(self.appconfig.Roll_subordinate))                     # 滚压电机地址
        self.lineEdit_5.setText(str(self.appconfig.Roll_pressure_pos))               # 滚动下压距离
        self.lineEdit_7.setText(str(self.appconfig.Roll_pos))                        # 滚动距离
        self.lineEdit_6.setText(str(self.appconfig.Vibrator_pos))                    # 振动器位置
        self.__appText('ui data init finished')

    # 启动io定时器,定时时间是1秒1次
    def _start_io_timer(self):
        self.io_timer.start(1000)

    # 停止定时器
    def _stop_io_timer(self):
        self.io_timer.stop()

    # io 定时器时间到，读取io
    def _IO_timer(self):
        self.io_timer.stop()
        th = Thread(target=self.__IO_TH)
        th.setDaemon(True)
        th.start()

    def __IO_TH(self):
        try:
            if self.jacquard_tester is None:
                self.__appText('jacquard_tester object not init', 2)
            if self.jacquard_tester.kmlio is None:
                self.__appText('io object not init', 2)

            # input
            self.changebackgoundEvent.emit(self.line_in1,
                                           self._get_background(self.jacquard_tester.kmlio.get_E_Stop()[0]))
            self.changebackgoundEvent.emit(self.line_in2,
                                           self._get_background(self.jacquard_tester.kmlio.get_start_button1()[0]))
            self.changebackgoundEvent.emit(self.line_in3,
                                           self._get_background(self.jacquard_tester.kmlio.get_start_button2()[0]))
            self.changebackgoundEvent.emit(self.lline_in4,
                                           self._get_background(self.jacquard_tester.kmlio.get_reset_button()[0]))
            self.changebackgoundEvent.emit(self.line_in5,
                                           self._get_background(self.jacquard_tester.kmlio.get_accelerated_up()[0]))
            self.changebackgoundEvent.emit(self.line_in6,
                                           self._get_background(self.jacquard_tester.kmlio.get_accelerated_down()[0]))
            self.changebackgoundEvent.emit(self.line_in7,
                                           self._get_background(self.jacquard_tester.kmlio.get_stretch_tensioning()[0]))
            self.changebackgoundEvent.emit(self.line_in8,
                                           self._get_background(self.jacquard_tester.kmlio.get_stretch_relax()[0]))
            self.changebackgoundEvent.emit(self.line_in9,
                                           self._get_background(self.jacquard_tester.kmlio.get_claw_clamp()[0]))
            self.changebackgoundEvent.emit(self.line_in10,
                                           self._get_background(self.jacquard_tester.kmlio.get_claw_loosen()[0]))
            self.changebackgoundEvent.emit(self.line_in11,
                                           self._get_background(self.jacquard_tester.kmlio.get_roll_warning()[0]))
            self.changebackgoundEvent.emit(self.line_in12,
                                           self._get_background(self.jacquard_tester.kmlio.get_loadcell_warning()[0]))
            self.changebackgoundEvent.emit(self.line_in13,
                                           self._get_background(self.jacquard_tester.kmlio.get_vacuo()[0]))
            self.changebackgoundEvent.emit(self.line_in14,
                                           self._get_background(self.jacquard_tester.kmlio.get_safty_raster()[0]))
            self.changebackgoundEvent.emit(self.line_in15,
                                           self._get_background(self.jacquard_tester.kmlio.get_foot_switch()[0]))
            self.changebackgoundEvent.emit(self.line_in16,
                                           self._get_background(self.jacquard_tester.kmlio.get_product_checked()[0]))

            # # output
            self.changedcheckedEvent.emit(self.chk_out1, self.jacquard_tester.kmlio.get_output(1)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out2, self.jacquard_tester.kmlio.get_output(2)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out3, self.jacquard_tester.kmlio.get_output(3)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out4, self.jacquard_tester.kmlio.get_output(4)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out5, self.jacquard_tester.kmlio.get_output(5)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out6, self.jacquard_tester.kmlio.get_output(6)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out7, self.jacquard_tester.kmlio.get_output(7)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out8, self.jacquard_tester.kmlio.get_output(8)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out9, self.jacquard_tester.kmlio.get_output(9)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out10, self.jacquard_tester.kmlio.get_output(10)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out11, self.jacquard_tester.kmlio.get_output(11)[0] == 0)
            self.changedcheckedEvent.emit(self.chk_out12, self.jacquard_tester.kmlio.get_output(12)[0] == 0)

            self.changedEvent.emit()
        except Exception, ex:
            self.__appText(ex.message, 2)
            self.__appText(u'请检查端口是否设置正确或io板卡是否连接', 2)

    def _get_background(self, value):
        if value == 1:
            return GREEN_background
        elif value == 0:
            return GRAY_backgroud
            # return RED_background
        else:
            return RED_background

    # 更新控件背景
    def __changebackgound(self, wedgit, backgroud):
        wedgit.setStyleSheet(backgroud)

    def __changedchecked(self, chk, cheked):
        if isinstance(chk, QCheckBox):
            chk.setChecked(cheked)

    def __changedEvent(self):
        self._start_io_timer()

    # textEdit信息更新
    # 1 默认颜色, 2 红色, 3=#00FFFF, 其它按默认色
    def __appendInfo(self, msg, color=1):
        #                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if color is False or color == 2:
            self.textEdit.append(u"""<HTML><font size="5" color="#FF0000">{0}</font> </HTML>""".format(msg))
        elif color == 3:
            self.textEdit.append(u"""<HTML><font size="5" color="#00FFFF">{0}</font> </HTML>""".format(msg))
        else:
            self.textEdit.append(u"""<HTML><font size="5" color="#00FF00">{0}</font> </HTML>""".format(msg))

    # 写信息
    def __appText(self, msg, color=1):
       self.appendInfo.emit(msg, color)

    # 面压loadcell数据采集
    def _rectangle_loadcell(self):
        text = self.pushButton.text()
        if isinstance(text, QtCore.QString):
            text = unicode(text.toUtf8(), 'utf-8', 'ignore')  # QString 的转换unicode编码
        # print type(text)
        if text == u'loadcell采集停止':
            self.pushButton.setText(garment_testui._translate("MainWindow", "loadcell采集", None))
            self._reading_loadcell = False
        else:
            self._reading_loadcell = True
            self.pushButton.setText(garment_testui._translate("MainWindow", "loadcell采集停止", None))
            th = Thread(target=self.__collect_loadcell)
            th.start()

    # loadcell 采集
    def __collect_loadcell(self):
        while self._reading_loadcell:
            rts = self.jacquard_tester.loadcell.ReadLocalCellSigle()
            self.__appText(str(rts), rts == -1)
            time.sleep(0.02)

    # Franklin Gothic Medium
    def _mcu_collect(self):
        QMessageBox.information(self, u'提示', u'未实现')

    # 滚压下压
    def _roll_down_run(self):
        if self.jacquard_tester is not None:
            pos = self.lineEdit_5.text()
            if len(pos) > 0:
                pos = int(pos)
                self.__appText('down pos = {0} start'.format(pos))
                try:
                    self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Push_down_subordinate, pos,
                                                             KML_tester_base.ACCELEROMETER,
                                                             KML_tester_base.DECELERATION, KML_tester_base.RATIO, True)
                    self.__appText('down pos = {0} end '.format(pos))
                    QMessageBox.information(self, 'info', 'run finished')
                except Exception, ex:
                    self.__appText('run exception :' + ex.message)
            else:
                QMessageBox.information(self, 'info', 'please input pos values')
                self.lineEdit_5.setFocus()
        else:
            self.__appText('jacquard_tester object do not init')

    # 滚压下压复位
    def _roll_down_reset(self):
        if self.jacquard_tester is not None:
            self.__appText('down reset start')
            try:
                self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Push_down_subordinate, 0,
                                                         KML_tester_base.ACCELEROMETER,
                                                         KML_tester_base.DECELERATION, KML_tester_base.RATIO, True)
                self.__appText('down reset ebd')
                QMessageBox.information(self, 'info', 'reset finished')
            except Exception, ex:
                self.__appText('run exception :' + ex.message)
        else:
            self.__appText('jacquard_tester object do not init')

    # 下压电机回home
    def _moon_press_home(self):
        if self.jacquard_tester is not None:
            self.__appText('press moon homeback start')
            try:
                self.jacquard_tester.moon_motor.SetMoonsHome(self.appconfig.Push_down_subordinate)
                self.__appText('press moon homeback ebd')
                QMessageBox.information(self, 'info', 'press moon homeback finished')
            except Exception, ex:
                self.__appText('press moon homgback exception :' + ex.message)
        else:
            self.__appText('jacquard_tester object do not init')

    # 滚动电机回home
    def _moon_roll_home(self):
        if self.jacquard_tester is not None:
            self.__appText('roll moon homeback start')
            try:
                self.jacquard_tester.moon_motor.SetMoonsHome(self.appconfig.Roll_subordinate)
                self.__appText('roll moon homeback ebd')
                QMessageBox.information(self, 'info', 'roll moon homeback finished')
            except Exception, ex:
                self.__appText('roll moon homgback run exception :' + ex.message)
        else:
            self.__appText('jacquard_tester object do not init')

    # 移动到振动器测试位置
    def _acc_run(self):
        if self.jacquard_tester is not None:
            pos = self.lineEdit_6.text()
            if len(pos) > 0:
                pos = int(pos)
                self.__appText('up pos = {0} start'.format(pos))
                try:
                    self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Roll_subordinate, pos,
                                                             KML_tester_base.ACCELEROMETER,
                                                             KML_tester_base.DECELERATION, KML_tester_base.RATIO, True)
                    self.__appText('move pos = {0} end '.format(pos))
                    QMessageBox.information(self, 'info', 'run finished')
                except Exception, ex:
                    self.__appText('run exception :' + ex.message)
            else:
                QMessageBox.information(self, 'info', 'please input pos values')
                self.lineEdit_6.setFocus()
        else:
            self.__appText('jacquard_tester object do not init')

    # 振动电机复位
    def _acc_reset(self):
        if self.jacquard_tester is not None:
            self.__appText('up reset start')
            try:
                self.jacquard_tester.moon_motor.MoveLine(self.appconfig.roll_subordinate, 0, KML_tester_base.ACCELEROMETER,
                                                         KML_tester_base.DECELERATION, KML_tester_base.RATIO, True)
                self.__appText('up reset ebd')
                QMessageBox.information(self, 'info', 'reset finished')
            except Exception, ex:
                self.__appText('run exception :' + ex.message)
        else:
            self.__appText('jacquard_tester object do not init')

    # 滚动测试起始位置
    def _roll_start_pos(self):
        if self.jacquard_tester is not None:
            pos = self.lineEdit.text()
            if len(pos) > 0:
                pos = int(pos)
                self.__appText('roll test tart pos = {0} start'.format(pos))
                try:
                    self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Roll_subordinate, pos,
                                                             KML_tester_base.ACCELEROMETER,
                                                             KML_tester_base.DECELERATION, KML_tester_base.RATIO, True)
                    self.__appText('roll run pos = {0} end '.format(pos))
                    QMessageBox.information(self, 'info', 'run finished')
                except Exception, ex:
                    self.__appText('run exception :' + ex.message)
            else:
                QMessageBox.information(self, 'info', 'please input pos values')
                self.lineEdit_7.setFocus()
        else:
            self.__appText('jacquard_tester object do not init')

    # 滚动运动
    def _roll_run(self):
        if self.jacquard_tester is not None:
            pos = self.lineEdit_7.text()
            if len(pos) > 0:
                pos = int(pos)
                self.__appText('roll run pos = {0} start'.format(pos))
                try:
                    self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Roll_subordinate, pos,
                                                             KML_tester_base.ACCELEROMETER,
                                                             KML_tester_base.DECELERATION, KML_tester_base.RATIO, True)
                    self.__appText('roll run pos = {0} end '.format(pos))
                    QMessageBox.information(self, 'info', 'run finished')
                except Exception, ex:
                    self.__appText('run exception :' + ex.message)
            else:
                QMessageBox.information(self, 'info', 'please input pos values')
                self.lineEdit_7.setFocus()
        else:
            self.__appText('jacquard_tester object do not init')

    # 滚动运动复位
    def _roll_reset(self):
        if self.jacquard_tester is not None:
            self.__appText('up reset start')
            try:
                self.jacquard_tester.moon_motor.MoveLine(self.appconfig.Roll_subordinate, 0, KML_tester_base.ACCELEROMETER,
                                                         KML_tester_base.DECELERATION, KML_tester_base.RATIO, True)
                self.__appText('up reset ebd')
                QMessageBox.information(self, 'info', 'reset finished')
            except Exception, ex:
                self.__appText('run exception :' + ex.message)
        else:
            self.__appText('jacquard_tester object do not init')

    def _save_config(self):
        QMessageBox.information(self, u'提示', u'功能未实现')         # funcation not completed'

    # 加速振动器数据采集
    def _accelerometer(self):
        text = self.pushButton_28.text()
        if isinstance(text, QtCore.QString):
            text = unicode(text.toUtf8(), 'utf-8', 'ignore')    # QString 的转换unicode编码
        # print type(text)
        if text == u'ACC停止':
            self.pushButton_28.setText(garment_testui._translate("MainWindow", "ACC采集", None))
            self._reading_acc = False
        else:
            self._reading_acc = True
            self.pushButton_28.setText(garment_testui._translate("MainWindow", "ACC停止", None))
            acc_th = Thread(target=self.__read_accelerometer)
            acc_th.setDaemon(True)
            acc_th.start()

    def __read_accelerometer(self):
        try:
            while self._reading_acc:
                acc_info = self.jacquard_tester.haptics_probe.read_data()
                self.__appText('temperature={0}'.format(acc_info.temperature))
                self.__appText('accelerated speed ={0},{1},{2}'.format(acc_info.xyz_acc[0], acc_info.xyz_acc[1], acc_info.xyz_acc[2]))
                self.__appText('angular speed ={0},{1},{2}'.format(acc_info.xyz_angle_acc[0], acc_info.xyz_angle_acc[1], acc_info.xyz_angle_acc[2]))
                self.__appText('angle = {0},{1},{2}'.format(acc_info.xyx_angle[0], acc_info.xyx_angle[1], acc_info.xyx_angle[2]))
                self.__appText('-'.center(100, '-'))
                # time.sleep(1)
        except Exception, ex:
            self.__appText('read acc data exception: '+ ex.message)
        finally:
            self.__appText('colllect finished')

    # 启动指示灯
    def _start_lamp(self, chk):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(1)[0]
        self.jacquard_tester.kmlio.set_start_lamp(1 if on_off==0 else 0)
        self._start_io_timer()

    # 复位指示灯
    def _reset_lamp(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(2)[0]
        self.jacquard_tester.kmlio.set_reset_lamp(1 if on_off==0 else 0)
        self._start_io_timer()

    # 三色指示灯绿色
    def _green_lamp(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(3)[0]
        self.jacquard_tester.kmlio.set_green(1 if on_off==0 else 0)
        self._start_io_timer()

    # 三色指示灯红色
    def _red_lamp(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(4)[0]
        self.jacquard_tester.kmlio.set_red(1 if on_off==0 else 0)
        self._start_io_timer()

    # 三色指示灯蓝色
    def _blue_lamp(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(5)[0]
        self.jacquard_tester.kmlio.set_blue(1 if on_off==0 else 0)
        self._start_io_timer()

    # 蜂鸣器
    def _buzzer(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(6)[0]
        self.jacquard_tester.kmlio.set_buzzer(1 if on_off==0 else 0)
        self._start_io_timer()

    # 加速度无杆气缸电磁阀上
    def _acc_cylinder_up(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(7)[0]
        self.jacquard_tester.kmlio.set_accelerated_up(1 if on_off==0 else 0)
        self._start_io_timer()

    # 加速度无杆气缸电磁阀下
    def _acc_cylinder_down(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(8)[0]
        self.jacquard_tester.kmlio.set_accelerated_down(1 if on_off==0 else 0)
        self._start_io_timer()

    # 张紧气缸
    def _stretch_cylinder(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(9)[0]
        self.jacquard_tester.kmlio.set_stretch_tensioning(1 if on_off==0 else 0)
        self._start_io_timer()

    # 夹爪气缸
    def _clamp_cylinder(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(10)[0]
        self.jacquard_tester.kmlio.set_stretch_relax(1 if on_off==0 else 0)
        self._start_io_timer()

    # 真空阀开关
    def _vacuum_switch(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(11)[0]
        self.jacquard_tester.kmlio.set_vacuum_switch(1 if on_off == 0 else 0)
        self._start_io_timer()

    # 清loadcell数据
    def _clear_loadcell(self):
        self._stop_io_timer()
        time.sleep(0.1)
        on_off = self.jacquard_tester.kmlio.get_output(12)[0]
        self.jacquard_tester.kmlio.set_loadcell_clear(1 if on_off == 0 else 0)
        self._start_io_timer()

    # 治具检测
    def _fix_check(self):
        try:
            self.stoptimerEvent.emit()  # 停止
            if self.jacquard_tester.test_step(1) and self.jacquard_tester.test_step(2):
            # if self.jacquard_tester.test_step(1):
                self._current_step = 3
                self.__appText('Fixture check ok')
                return True
            else:
                self.__appText('Fixture check fail')
                # QMessageBox.information(self, 'info', 'please execute step 2 pressure_test')
        except Exception, ex:
            self.__appText('Fixture check exception :' + ex.message)
        finally:
            self.changedEvent.emit()  # 开始
        return False

    # 滚压测试
    def _roll_test(self):
        try:
            self.stoptimerEvent.emit()  # 停止
            if self._current_step == 3:
                if self.jacquard_tester.test_step(3):
                    self._current_step = 4
                    self.__appText('roll_test ok')
                    return True
                else:
                    self.__appText('roll_test fail')
            else:
                self.__appText('please execute step 2 pressure_test')
                # QMessageBox.information(self, 'info', 'please execute step 2 pressure_test')
        except Exception,ex:
            self.__appText('roll_test exception :' + ex.message)
        finally:
            self.changedEvent.emit()  # 开始
        return False

    # 振动测试
    def _acc_test(self):
        try:
            self.stoptimerEvent.emit()  # 停止
            if self._current_step == 4:
                if self.jacquard_tester.test_step(4):
                    self._current_step = 5
                    self.__appText('vibration_test ok')
                    return True
                else:
                    self.__appText('vibration_test fail')
            else:
                self.__appText('please execute step 3 roll_test')
                # QMessageBox.information(self, 'info', 'please execute step 3 roll_test')
        except Exception, ex:
            self.__appText('vibration_test exception :' + ex.message)
        finally:
            self.changedEvent.emit()  # 开始
        return False

    # 测试结束
    def _test_finished(self):
        try:
            # reply = QMessageBox.question(self, 'info', 'Function not implemented ', QMessageBox.Yes | QMessageBox.No)
            # 复位
            self.stoptimerEvent.emit()  # 停止
            if self.jacquard_tester.reset():
                self._current_step = 0
                self.__appText('reset ok')
                return True
            else:
                self.__appText('reset fail')
        except Exception, ex:
            self.__appText('reset exception :' + ex.message)
        finally:
            self.changedEvent.emit()  # 开始
        return False

    def __test(self, loop):
        try:
            while self._testing:
                test_status = self._fix_check()
                if test_status and self._testing:
                    test_status = self._roll_test()
                if test_status and self._testing:
                    test_status = self._acc_test()

                self._test_finished()
                self._test_count += 1
                if loop is False:
                    break
                self.__appText('test count = {0} finished'.format(self._test_count).center(100, '-'))
                time.sleep(5)  # 间隔5秒进行下一次
        except Exception,ex:
            self.__appText("loop_test_th exception:" + ex.message)
        finally:
            self.__appText('test finished')
            self._start_io_timer()
        self._stop_io_timer()

    # 自动测试
    def _auto_test(self):
        self._testing = True
        th = Thread(target=self.__test, args=(False,))
        th.setDaemon(True)
        th.start()

    # 循环测试
    def _loop_test(self):
        text = self.btn_loop_test.text()
        if isinstance(text, QtCore.QString):
            text = unicode(text.toUtf8(), 'utf-8', 'ignore')  # QString 的转换unicode编码
        if text == u'停止':
            self._testing = False
            self.btn_loop_test.setText(garment_testui._translate("", "循环测试", None))
        else:
            self.btn_loop_test.setText(garment_testui._translate("", "停止", None))
            self._test_count = 0
            self._testing = True
            loop_test_th = Thread(target=self.__test, args=(True,))
            loop_test_th.setDaemon(True)
            loop_test_th.start()

    # 复位
    def _reset(self):
        try:
            # reply = QMessageBox.question(self, 'info', 'Function not implemented ', QMessageBox.Yes | QMessageBox.No)
            # 复位
            self.stoptimerEvent.emit()  # 停止
            if self.jacquard_tester.backhome():
                self._current_step = 0
                self.__appText('reset ok')
                return True
            else:
                self.__appText('reset fail')
        except Exception, ex:
            self.__appText('reset exception :' + ex.message)
        finally:
            self._start_io_timer()  # 开始
        return False


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui = Garment_MainWindow()
    ui.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
    ui.show()
    sys.exit(app.exec_())