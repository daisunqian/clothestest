# -*- coding=utf-8 -*-

from PyQt4.QtCore import pyqtSignal, QThread
from PyQt4 import QtGui
import time
import datetime
import serial.tools.list_ports
import os
from Comm.CSVHelper import CSVHelper
from Comm.AffirmWindow import AffirmWindow

HEADER = ['名称', '判定值', '采集值', '状态', '信息', '测试时间', '测试人员']


class IProduce(QThread):
    # 信息显示信号
    # (信息，状态)
    display_msg = pyqtSignal(str, bool)
    # 测试步骤开始信号
    # 参数：步骤名称
    test_step_start = pyqtSignal(str)
    # 测试步骤结束信号
    # 参数：步骤名称, 判断值, 采集值,状态，信息
    test_step_finished = pyqtSignal(str, str, str, bool, str)
    # 通知调用打开UI
    # 参数: 标题, 提示信息
    messag_box_open = pyqtSignal(str, str)

    # appconfig 配置文件操作对象
    def __init__(self, appconfig):
        super(IProduce, self).__init__()
        self.appconfig = appconfig
        self.csv_file = None
        self.csv_dir = None
        self.iswite = True               # true才写入文件
        self._message_bos_rst = False    # 测试打开窗口结果, True成功，False失败
        self._message_box_close = False  # True表示窗口关闭返回,否则还在打开状态
        self._init_dir()
        self._get_csv()
        self._write_csv(u'名称', '贺', '2', False, 'test')

    def _init_dir(self):
        try:
            self.csv_dir = self.appconfig.Produce_dir
            if os.path.exists(self.csv_dir) is False:
                os.mkdir(self.csv_dir)
        except Exception, ex:
            self.csv_dir = r'C:\produce_summary'

    def _get_csv(self):
        try:
            name = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
            file_path = "{0}\{1}".format(self.csv_dir, name)
            if self.csv_file is None:
                self.csv_file = CSVHelper(file_path, HEADER)
            else:
                self.csv_file.create_csv(file_path, HEADER)
            self._on_display_msg(self.csv_file.message)
        except Exception, ex:
            self._on_display_msg(u'创建文件{0}失败,{1}'.format(name, ex.message), False)

    def _on_messag_box_open(self, title, info):
        self.messag_box_open.emit(title, info)
        self._message_box_close = False
        while self._message_box_close is False:
            time.sleep(1)
        return self._message_bos_rst

    # 触发display_msg信号
    def _on_display_msg(self, msg, status=True):
        self.display_msg.emit(msg, status)

    # 触发test_step_start信号
    def _on_test_step_start(self, name):
        self.test_step_start.emit(name)

    # 触发test_step_finished信号
    def _ontest_step_finished(self, name, limit, value, status, msg, uname=None):
        self.test_step_finished.emit(name, limit, value, status, msg)
        self._write_csv(name, limit, value, status, msg, uname)

    # 写文件
    def _write_csv(self, name, limit, value, status, msg, uname=None):
        if self.iswite is False:
            self._on_display_msg(u'测试文件未写入, 因为程序写入标志关闭即iswite=False', False)
            return
        name_str = name
        if isinstance(name, unicode):
            name_str = name.encode('utf-8')
        limit_str = limit
        if isinstance(limit, unicode):
            limit_str = limit.encode('utf-8')
        value_str = value
        if isinstance(value, unicode):
            value_str = value.encode('utf-8')
        msg_str = msg
        if isinstance(msg, unicode):
            msg_str = msg.encode('utf-8')
        uname_str = uname
        if isinstance(uname, unicode):
            uname_str = uname.encode('utf-8')
        if self.csv_file is None:
            self._get_csv()
        if self.csv_file is not None:
            self.csv_file.write("{0},{1},{2},{3},{4},{5},{6}".format(name_str, limit_str, value_str, status, msg_str,
                                                                     datetime.datetime.now(), uname_str))

    # 获取pc所有可用端口
    def _get_ports(self):
        port_list = []
        ports_obj = serial.tools.list_ports.comports()
        for port_obj in ports_obj:
            port_list.append(list(port_obj)[0])
        return port_list

    # 询问对话框
    def question(self, title, info, img=None, parent=None):
        self._message_box_close = False
        win = AffirmWindow(parent)
        win.setimg(img)
        win.set_display(title + "\n" + info)
        win.exec_()
        self._message_box_close = True
        self._message_bos_rst = win.result()
        return self._message_bos_rst

        # self._message_box_close = False
        # yes = QtGui.QMessageBox.question(parent, title, info, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        # self._message_box_close = True
        # self._message_bos_rst = yes == QtGui.QMessageBox.Yes
        # return yes == QtGui.QMessageBox.Yes

    def run(self):
        self._get_csv()
        self.start_check()
        # print self._on_messag_box_open('1', '11')
        # print self._on_messag_box_open('2', '22')
        # print self._on_messag_box_open('3', '33')

    # 开始执行测试
    def start_check(self):
       pass


if __name__ == '__main__':
    from FixtureControl.APPConfigparse import APPConfigparse
    appconfig = APPConfigparse(r'../config.ini')
    produce = IProduce(appconfig)

    # produce.start()
    # while True:
    #     pass