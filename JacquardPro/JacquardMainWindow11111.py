# -*- coding:utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtGui import QBrush, QColor
from PyQt4.QtCore import QTimer, pyqtSignal, Qt
# from PyQt4 import Qt
from ui import Ui_MainWindow
from FixtureControl.APPConfigparse import APPConfigparse
from FixtureControl.Limit import LimitConfig
from FixtureControl.JacpuardTestFactory import JacpuardTestFactory
import datetime
# from threading import Thread
from FixtureControl import IJacquardTest
from Comm import ThreadHelper, CSVHelper
from login import Login
from PortConfig import PortConfig
from ui_demo.ResultWindowd import ResultWindow
from ui_demo import Stylesheets
import serial
from threading import Thread
import time

# 2019-03-21 V1,0.0.4---liyunhe
# 振动时间调整成2秒
# 增加mcu通讯执行命令(端口检测命令，开始测试命令，结束测试命令)
# 振动前发送"*"结束r或是t命令上传
# datagridview修改成自读模式
# 振动测试增加重测操作

# 2019-03-22 V1.0.0.5---liyunhe
# 修改振动测试bug（acc通讯不正常的情况下，可能会进入死循环）

# 2019-03-26 V1.0.0.6---liyuunhe
# 修改KS运动流程
# 修改KS数据分析算发流程---raw count data ,difference数据, sensor L0-L11

# 2019-03-27 V1.0.0.7---liyunhe
# 修改KS和KY背包测试接触力的过程

# 2019-03-28 V1.0.0.8---liyunhe
# 修改KS和KY第一段结束N为1N


APP_NAME = 'innorev Application'
APP_VERSION = "V1.0.0.8"
TEST_INIT = "IDLE"
TEST_TESTING = "TESTING"
TEST_PASS = "PASS"
TEST_FAIL = "FAIL"
HEADER_ITEM = 'item'
HEADER_VALUE = 'value'
HEADER_STATUS = 'status'
HEADER_LIMIT = 'limit'
HEADER_CAMERA_SN = 'SN'
HEADER_CAMERA_1 = "OPT_1"
HEADER_CAMERA_2 = "OPT_2"
RED_BRUSH = QBrush(QColor(255, 0, 0))
GREEN_BRUSH = QBrush(QColor(0, 255, 0))
BLUE_BRUSH = QBrush(QColor(0, 0, 255))
YELLOW_BRUSH = QBrush(QColor(255, 255, 0))
GRAY_backgroud = "background-color:rgb(192, 192, 192)"
YELLOW_background = "background-color:rgb(255,255,0)"
RED_background = "background-color:rgb(255,0,0)"
GREEN_background = "background-color:rgb(0,255,0)"


class JacquardMainWindow(Ui_MainWindow):
    appendInfo = pyqtSignal(str, int)  # 修改信息

    def __init__(self):
        super(JacquardMainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 初始化配置文件对象
        self.appconfig = APPConfigparse(r'./config.ini')
        self.limitConfig = LimitConfig(r'./limit.ini')
        # 自定义信号连接
        self.appendInfo.connect(self.__appendInfo)
        self.__appText("config init success")
        # 窗口信息初始化
        self.setWindowIcon(QIcon('./resource/app.png'))
        self.setWindowTitle(APP_NAME)
        self.top_text.setText("{0}.{1}  {2}".format(APP_NAME, self.appconfig.Test_type, APP_VERSION))
        # 状态栏初始化函数
        self.init_statusbar()
        self.__InitTableView()
        # UI 控件初始化
        self._init_ui()
        # self.lab_result.hide()  # 隐藏不使用
        # 对象初始化
        self.current_summary = []                 # 当前测试的测试项结果信息集合,要将该数据写入文件中
        self.jacquard_tester = JacpuardTestFactory.create_JacpuardTest(self.appconfig.Test_type,
                                                                       self.appconfig, self.limitConfig)
        if self.jacquard_tester is None:
            self.__appText("test object init fail, test type {0}".format(self.appconfig.Test_type), False)
        else:
            # 创建测试数据存储路径
            self.jacquard_tester.summary_dir = self._create_summary_dir()
            self.__appText(self.jacquard_tester.summary_dir)

            self.jacquard_tester.test_start.connect(self.__test_start)
            self.jacquard_tester.test_end.connect(self.__test_end)
            self.jacquard_tester.read_sn.connect(self.__read_sn)
            self.jacquard_tester.item_start.connect(self.__item_start)
            self.jacquard_tester.item_end.connect(self.__item_end)
            self.jacquard_tester.manual_window.connect(self.__manual_window)
            self.jacquard_tester.display_msg.connect(self.__display_msg)
            self.__appText("test object init success, test type {0}".format(self.appconfig.Test_type))
            port_list = self._get_ports()
            self.__appText(str(port_list))
            init_st = self.jacquard_tester.check_connect(auto=True, port_list=port_list)
            # init_st = self.jacquard_tester.check_connect()
            self.__set_statusbar(init_st)

        # 测试相关
        self._ResultWindow = ResultWindow()
        self.current_test_thread = None          # 当前测试线程
        self._testing = False                    # true测试中，否则处于空闲状态
        self.dut1_items = {}                     # 1号dut测试项
        self.dut1_timer = QTimer(self)
        self.dut1_timer.timeout.connect(self.__dut1_timer)
        self._reset_happen_time = time.time()


    # 重写
    def closeEvent(self, *args, **kwargs):
        reply = QMessageBox.question(self, 'question', 'close window ?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 清理操作
            self._stop_device_moniter()
            args[0].accept()  # 放弃关闭窗口
        else:
            args[0].ignore()    # 放弃关闭窗口

    def maxwindow(self):
        # 得到桌面控件
        desktop = QApplication.desktop()
        # 得到屏幕可显示尺寸
        rect = desktop.availableGeometry()
        self.setGeometry(rect)

    # 创建summary路径
    def _create_summary_dir(self):
        import os
        _dir = '.\\'
        if self.appconfig is not None:
            # 生成当日文件路径
            _dir = self.appconfig.Summary_dir

        _dir += "\\" + datetime.datetime.now().strftime("%Y%m%d")
        if os.path.exists(_dir) is False:
            os.makedirs(_dir)
        return _dir

    # 软件启动时找home以及复位
    def _start_reset(self):
        pass
    # 获取pc所有可用端口
    def _get_ports(self):
        port_list = []
        ports_obj = serial.tools.list_ports.comports()
        for port_obj in ports_obj:
            port_list.append(list(port_obj)[0])
        return port_list

    def _portchanged(self, ptype, port, baudrate):
        print 'port changed'

    # 初始化ui 控件
    def _init_ui(self):
        # self.statusbar.setStyleSheet("background-color:rgb(255, 251, 240);color:rgb(0,0,0)")
        # self.groupBox.setStyleSheet(GRAY_backgroud)
        # self.groupBox.setTitle('')        # 1#  test result
        # self.groupBox_5.setStyleSheet(GRAY_backgroud)
        # self.groupBox_5.setTitle('')       # 2# test result
        # self.groupBox_3.setTitle('')
        # self.groupBox_3.setStyleSheet('border-width:0;border-style:outset')
        self.lab_result.setText(TEST_INIT)
        self.linesn1.setReadOnly(True)
        # self.linesn2.setReadOnly(True)
        self.linetime1.setReadOnly(True)
        # self.linetime2.setReadOnly(True)

        # self.start.setStyleSheet("background-color: rgb(164, 185, 255);"
        #                             "border-color: rgb(170, 150, 163);"
        #                             "font: 75 12pt \"Arial Narrow\";"
        #                             "color: rgb(126, 255, 46);")
        #
        # self.reset.setStyleSheet("background-color: rgb(164, 185, 255);"
        #                          "border-color: rgb(170, 150, 163);"
        #                          "font: 75 12pt \"Arial Narrow\";"
        #                          "color: rgb(126, 255, 46);")

        icon = QIcon()
        icon.addPixmap(QPixmap("./resource/close.ico"), QIcon.Normal, QIcon.Off)
        self.btn_exit.setIcon(icon)
        self.btn_exit.setStyleSheet(Stylesheets.btn_style_close)

        icon = QIcon()
        icon.addPixmap(QPixmap("./resource/start.ico"), QIcon.Normal, QIcon.Off)
        self.start.setIcon(icon)
        self.start.setStyleSheet(Stylesheets.btn_style_Cyan)

        icon = QIcon()
        icon.addPixmap(QPixmap("./resource/reset.ico"), QIcon.Normal, QIcon.Off)
        self.reset.setIcon(icon)
        self.reset.setStyleSheet(Stylesheets.btn_style_Cyan)

        self.start.clicked.connect(self.__start_button)
        self.reset.clicked.connect(self.__reset_button)
        self.btn_exit.clicked.connect(self.__close_window)

    # 状态栏初始化
    def init_statusbar(self):
        # # 隐藏TabWidget的第二个Tab,取消屏蔽可恢复
        # self.camera2.deleteLater()
        # *********相邻Label设置固定的间隔？？？
        # self.label1.setAcceptDrops(True)
        # 创建label
        self.label1_status = PortLable(1)
        self.label1_status.portchanged.connect(self._portchanged)
        self.label2_status = PortLable(2)
        self.label2_status.portchanged.connect(self._portchanged)
        self.label3_status = PortLable(3)
        self.label3_status.portchanged.connect(self._portchanged)
        self.label4_status = PortLable(4)
        self.label4_status.portchanged.connect(self._portchanged)
        self.label5_status = PortLable(5)
        self.label5_status.portchanged.connect(self._portchanged)
        self.label6_status = PortLable(6)
        self.label6_status.portchanged.connect(self._portchanged)
        self.label7_status = PortLable(7)
        self.label7_status.portchanged.connect(self._portchanged)
        self.label8_status = PortLable(8)
        self.label8_status.portchanged.connect(self._portchanged)

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

    # 初始化tableview
    def __InitTableView(self):
        # 1#camera
        self.camera1_standard = QStandardItemModel()
        self.table_test_items.setModel(self.camera1_standard)
        self.camera1_standard.setHorizontalHeaderItem(0, QStandardItem(HEADER_ITEM))
        self.camera1_standard.setHorizontalHeaderItem(1, QStandardItem(HEADER_VALUE))
        self.camera1_standard.setHorizontalHeaderItem(2, QStandardItem(HEADER_STATUS))
        self.camera1_standard.setHorizontalHeaderItem(3, QStandardItem(HEADER_LIMIT))
        # self.table_test_items.setColumnWidth(0, 300)
        # self.table_test_items.setColumnWidth(1, 300)
        # self.table_test_items.setColumnWidth(2, 200)
        # self.table_test_items.setColumnWidth(3, 300)
        # self.table_test_items.horizontalHeader().setStretchLastSection(True)
        #
        # ResizeMode：
        # QHeaderView::Interactive ：0  用户可设置，也可被程序设置成默认大小
        # QHeaderView::Fixed       ：2  用户不可更改列宽
        # QHeaderView::Stretch     ：1  根据空间，自动改变列宽，用户与程序不能改变列宽
        # QHeaderView::ResizeToContents：3 根据内容改变列宽，用户与程序不能改变列宽
        # 注意：ResizeMode被设置为1, 3 时， void QTableView::​setColumnWidth(int column, int width）的效果不会被执行，即不能定义某一列的列宽
        self.table_test_items.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        # self.table_test_items.verticalHeader().setDefaultSectionSize(50)
        # self.table_test_items.verticalHeader().setMinimumSectionSize(30)

    # 设置1# dut 测试结果到ui
    # sn
    # test_status=None，表示不测试，bool值表示测试结果
    # testing=true表示测试中，其它两个值无效
    def _set_dut1_result(self, sn, test_status, testing=False):
        if testing:
            self.lab_result.setStyleSheet(YELLOW_background)
            # self.widget_2.setStyleSheet(YELLOW_background)
            self.lab_result.setText(TEST_TESTING)
        else:
            # msg = '1#\n' + (sn+"\n" if sn is not None and len(sn)>0 else '')
            msg = (sn + "  " if sn is not None and len(sn) > 0 else '')
            if test_status is None:
                self.lab_result.setStyleSheet(GRAY_backgroud)
                # self.widget_2.setStyleSheet(GRAY_backgroud)
                self.lab_result.setText(TEST_INIT)
            elif test_status is True:
                self.lab_result.setStyleSheet(GREEN_background)
                # self.widget_2.setStyleSheet(GREEN_background)
                self.lab_result.setText(msg + TEST_PASS)
            elif test_status is False:
                self.lab_result.setStyleSheet(RED_background)
                # self.test_title_layout.setStyleSheet(RED_background)
                self.lab_result.setText(msg + TEST_FAIL)

            # self._ResultWindow = ResultWindow()
            size = self.geometry()
            self._ResultWindow.setwidth(size.width(), size.height())
            self._ResultWindow.setResult(test_status)
            self._ResultWindow.show()

        # self.sn1.setStyleSheet("background-color: rgb(226, 226, 226);")
        # self.linesn1.setStyleSheet("background-color: rgb(226, 226, 226);")
        # self.time1.setStyleSheet("background-color: rgb(226, 226, 226);")
        # self.linetime1.setStyleSheet("background-color: rgb(226, 226, 226);")
        # self.start.setStyleSheet("background-color: rgb(226, 226, 226);")
        # self.reset.setStyleSheet("background-color: rgb(226, 226, 226);")

    # 设置2# dut 测试结果到ui
    # sn
    # test_status=None，表示不测试，bool值表示测试结果
    # testing=true表示测试中，其它两个值无效
    def _set_dut2_result(self, sn, test_status, testing=False):
        pass
        # if testing:
        #     self.groupBox_5.setStyleSheet(YELLOW_background)
        #     self.result_camera_2.setText('2#\n' + TEST_TESTING)
        # else:
        #     msg = '2#\n' + (sn+"\n" if sn is not None and len(sn)>0 else '')
        #     if test_status is None:
        #         self.groupBox_5.setStyleSheet(GRAY_backgroud)
        #         self.result_camera_2.setText(TEST_INIT)
        #     elif test_status is True:
        #         self.groupBox_5.setStyleSheet(GREEN_background)
        #         self.result_camera_2.setText(msg + TEST_PASS)
        #     elif test_status is False:
        #         self.groupBox_5.setStyleSheet(RED_background)
        #         self.result_camera_2.setText(msg + TEST_FAIL)

    # 设备信号产生
    def __signal_happen(self, signal):
        self.__appText('singal happen {0}'.format(signal), 3)
        # if signal == IJacquardTest.START_SIGNAL:
        #     if self._testing is False:
        #         self._stop_device_moniter()        # 测试开始前，将信号监视关闭
        #         self._testing = True
        #         self.current_test_thread = Thread(target=self.jacquard_tester.start_test)
        #         self.current_test_thread.setDaemon(True)
        #         self.current_test_thread.start()
        if signal == IJacquardTest.RESET_SIGNAL:
            self.__appText('reset singal happen {0}'.format(signal), 3)
            self.jacquard_tester.stop_test()
            # 进行复位
            self.jacquard_tester.reset()
            # if time.time() - self._reset_happen_time > 60:
            #     self.jacquard_tester.reset()
        elif signal == IJacquardTest.E_STOP_SIGNAL:
            self.__appText('e-stop singal happen {0}'.format(signal), 3)
            self.jacquard_tester.stop_test()
        else:
            self.__appText('invalid signal {0}'.format(str(signal)))

    # 开始测试信号处理
    def __test_start(self):
        self.current_summary = []
        self._ResultWindow.close()
        icon = QIcon()
        icon.addPixmap(QPixmap("./resource/stop.ico"), QIcon.Normal, QIcon.Off)
        self.start.setIcon(icon)
        self.start.setText('stop')
        self.start.setStyleSheet(Stylesheets.btn_style_red)
        self.__appText('start test', 3)
        self._set_dut1_result(None, None, True)
        self.__clear_camera1_tableitems()
        self.__start_dut1_timer()

    # 采集到sn信号处理
    def __read_sn(self, sn):
        self.linesn1.setText(sn)

    # 测试结束信号处理
    def __test_end(self, sn, test_status):
        self.__stop_dut1_timer()
        self._set_dut1_result(sn, test_status)
        icon = QIcon()
        icon.addPixmap(QPixmap("./resource/start.ico"), QIcon.Normal, QIcon.Off)
        self.start.setIcon(icon)
        self.start.setText('start')
        self.start.setStyleSheet(Stylesheets.btn_style_Cyan)
        self._testing = False
        self._start_device_moniter()         # 上1次测试结束，打开信号监视,屏蔽测试
        # summary数据写入文件
        # self.current_summary
        if len(sn) > 0:
            ls = [sn, self.jacquard_tester.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                  self.jacquard_tester.end_time.strftime("%Y-%m-%d %H:%M:%S"), "PASS" if test_status else "FAIL"]
            ls.extend(self.current_summary)
            header = "SN,start_time,end_time,result"
            csv_helper = CSVHelper.CSVHelper(self.jacquard_tester.get_summary_file(), header)
            csv_helper.write(ls)

    # 测试项开始信号
    def __item_start(self, item):
        self.add_DUT1(item)

    # 测试项测试结束信息
    def __item_end(self, item, status, value, message, limit_str):
        self.update_DUT1(item, value, status, message, limit_str)

    def __manual_window(self, title, info):
        self.jacquard_tester.open_manual_window(title, info, r'.\\resource\\no_img.jpg', self)

    # 信息
    def __display_msg(self, msg, status):
        self.__appText(msg, 1 if status is True else 2)

    # 添加1#DUT测试项
    def add_DUT1(self, step):
        # 测试项，数据，状态， limit(4列)
        if self.dut1_items.has_key(step) is False:
            col_list = []
            item = QStandardItem(step)
            item.setEditable(False)
            col_list.append(item)
            item = QStandardItem('')
            item.setEditable(False)
            col_list.append(item)
            item = QStandardItem('')
            item.setEditable(False)
            col_list.append(item)
            item = QStandardItem('NO')
            item.setEditable(False)
            col_list.append(item)
            self.dut1_items[step] = dict(zip([HEADER_ITEM, HEADER_VALUE, HEADER_STATUS, HEADER_LIMIT], col_list))
            rowindex = len(self.dut1_items) - 1
            for colindx, item in enumerate(col_list):
                self.camera1_standard.setItem(rowindex, colindx, item)

            self.table_test_items.selectRow(rowindex)

    # 修改1#camera数据项数据
    def update_DUT1(self, step, data, status, msg, limit_str='No'):
        self.__appText("{0}-{1}-{2}".format(step, data, msg), status)
        # step_limit = self._ParaseLimit.get_limit(str(step))       # 门限值

        if status is False:
            self.current_summary.append("{0} Fail value={1} limit:{2}".format(step, data, limit_str))

        if self.dut1_items.has_key(step) is False:
            self.add_DUT1(step)

        if self.dut1_items.has_key(step) is True:
            col_list = self.dut1_items[step]
            # 因为col_list这个字典里的每个key对应的value值类型都为QStandardItem,setText()可用
            col_list[HEADER_VALUE].setText(str(data))
            col_list[HEADER_STATUS].setText(str(status))  # 根据status(bool) 显示不同数据
            col_list[HEADER_LIMIT].setText(limit_str)
            # col_list[HEADER_LIMIT].setText(step_limit)
            if status:
                col_list[HEADER_STATUS].setBackground(GREEN_BRUSH)
                col_list[HEADER_ITEM].setBackground(GREEN_BRUSH)
                col_list[HEADER_VALUE].setBackground(GREEN_BRUSH)
                col_list[HEADER_LIMIT].setBackground(GREEN_BRUSH)
            else:
                col_list[HEADER_STATUS].setBackground(RED_BRUSH)
                col_list[HEADER_ITEM].setBackground(RED_BRUSH)
                col_list[HEADER_VALUE].setBackground(RED_BRUSH)
                col_list[HEADER_LIMIT].setBackground(RED_BRUSH)

    # 1#camera 数据清除
    def __clear_camera1_tableitems(self):
        self.camera1_standard.removeRows(0, self.camera1_standard.rowCount())
        self.dut1_items.clear()

    # 开始检测设备start button信号
    def _start_device_moniter(self):
        return True
        # if self.jacquard_tester.get_monitor() is False:
        #     monitor_th = Thread(target=self.jacquard_tester.check_signal)
        #     monitor_th.setDaemon(True)
        #     monitor_th.start()
        #     self.__appText('start singal moniter...')
        #     if self.jacquard_tester.get_monitor() is False:
        #         self.__appText('start singal moniter fail')
        #         self.start.setText('moniter')
        # else:
        #     self.__appText('singal moniter open')

    # 关闭信号监视
    def _stop_device_moniter(self):
        return True
        # self.__appText('stop signal moniter')
        # if self.jacquard_tester is not None:
        #     self.jacquard_tester.stop_check()

    # dut 计时器
    def __dut1_timer(self):
        self.dut1_op_time += 1
        self.linetime1.setText(str(self.dut1_op_time) + "sec")

    # 开始1#DUT定时器
    def __start_dut1_timer(self):
        self.dut1_op_time = 0
        self.dut1_timer.start(1000)

    # 停止1#DUT定时器
    def __stop_dut1_timer(self):
        self.dut1_timer.stop()

    def __start_button(self):
        text = self.start.text()
        print text
        self.jacquard_tester.start_test()
        return True

    def __reset_button(self):
        print 111111
        return True

    def __close_window(self):
        print 'close'
        self.close()

    # 初始化信息显示到状态栏
    def __set_statusbar(self, init_st):
        self.label1_status.setText(init_st[0][1])
        if init_st[0][0]:
            self.label1_status.setStyleSheet(GREEN_background)
        else:
            self.label1_status.setStyleSheet(RED_background)

        # self.label2_status.setText(init_st[1][1])
        # if init_st[1][0]:
        #     self.label2_status.setStyleSheet(GREEN_background)
        # else:
        #     self.label2_status.setStyleSheet(RED_background)

        # self.label3_status.setText(init_st[2][1])
        # if init_st[2][0]:
        #     self.label3_status.setStyleSheet(GREEN_background)
        # else:
        #     self.label3_status.setStyleSheet(RED_background)
        #
        # self.label4_status.setText(init_st[3][1])
        # if init_st[3][0]:
        #     self.label4_status.setStyleSheet(GREEN_background)
        # else:
        #     self.label4_status.setStyleSheet(RED_background)

        # self.label5_status.setText(init_st[4][1])
        # if init_st[4][0]:
        #     self.label5_status.setStyleSheet(GREEN_background)
        # else:
        #     self.label5_status.setStyleSheet(RED_background)

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

        # textEdit信息更新
        # 1 默认颜色, 2 红色, 3=#00FFFF, 其它按默认色
    def __appendInfo(self, msg, color=1):
        if color is False or color == 2:
            self.message.append(u"""<HTML><font size="5" color="#FF0000">{0}:{1}</font> </HTML>""".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
        elif color == 3:
            self.message.append(u"""<HTML><font size="5" color="#00FFFF">{0}:{1}</font> </HTML>""".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
        else:
            self.message.append(u"""<HTML><font size="5" color="#00FF00">{0}:{1}</font> </HTML>""".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))

    # 写信息
    # 1 默认颜色, 2 红色, 3=#00FFFF, 其它按默认色
    def __appText(self, msg, color=1):
        try:
            self.appendInfo.emit(msg, color)
        except Exception, ex:
            print ex
        # if color is False or color == 2:
        #     self.message.append(u"""<HTML><font size="5" color="#FF0000">{0}:{1}</font> </HTML>""".format(
        #         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(msg).encode('utf-8')))
        # elif color == 3:
        #     self.message.append(u"""<HTML><font size="5" color="#00FFFF">{0}:{1}</font> </HTML>""".format(
        #         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(msg).encode('utf-8')))
        # else:
        #     self.message.append(u"""<HTML><font size="5" color="#00FF00">{0}:{1}</font> </HTML>""".format(
        #         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(msg).encode('utf-8')))


# 重写label的鼠标双击事件处理
# 用来编辑通讯端口
class PortLable(QLabel):
    # 端口更改信号
    # 参数（类型， 端口，波特率）
    portchanged = pyqtSignal(int, str, int)

    def __init__(self, port_type, parent=None):
        super(PortLable, self).__init__(parent)
        self.port_type = port_type

    def mouseDoubleClickEvent(self, e):
        text = 'port config'
        if self.port_type == 1:
            text = 'io port config'
        elif self.port_type == 2:
            pass
        elif self.port_type == 3:
            pass
        elif self.port_type == 4:
            pass
        elif self.port_type == 5:
            pass
        elif self.port_type == 6:
            pass
        elif self.port_type == 7:
            pass
        portwin = PortConfig(text)
        if portwin.exec_() == 1:
            self.portchanged.emit(self.port_type, portwin.currentport, portwin.currentbaudrate)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    loginwin = Login()
    isok = loginwin.exec_()
    if isok == 1:
        ui = JacquardMainWindow()
        # ui.showMaximized()
        ui.maxwindow()
        ui.show()
        sys.exit(app.exec_())