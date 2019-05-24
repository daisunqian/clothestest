# -*- coding:utf-8 -*-

import sys
import datetime
from PyQt4 import QtGui, QtCore
from ui_demo import ProduceCheckui
from FixtureControl.APPConfigparse import APPConfigparse
from FixtureControl.Limit import LimitConfig
from Produce import ProduceFactory

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class ProduceCheckWin(ProduceCheckui.Ui_Form):
    appendInfo = QtCore.pyqtSignal(str, int)  # 修改信息

    def __init__(self):
        super(ProduceCheckWin, self).__init__()
        # 初始化配置文件对象
        self.appconfig = APPConfigparse(r'./config.ini')
        self.limitConfig = LimitConfig(r'./limit.ini')
        # KML_garment_Produce.KML_garment_Produce(self.appconfig)
        self.produce_check = ProduceFactory.creat_produce(1, self.appconfig)
        self.produce_check.display_msg.connect(self.__appText)
        self.produce_check.messag_box_open.connect(self._test_window)
        self.produce_check.test_step_start.connect(self._test_step_start)
        self.produce_check.test_step_finished.connect(self._and_item)
        self._init_datagrid()
        self._init_event()

    def _init_datagrid(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels([u'名称', u'判断值', u'采集值', u'状态', u'信息'])
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)    # 自适应列宽
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

    #  添加一行数据
    def _and_item(self, name, limit, value, status, msg):
        # self._test_result.append([name, limit, value, status, msg])
        new_row_index = self.tableWidget.rowCount()
        self.tableWidget.insertRow(new_row_index)

        back_color = QtGui.QColor(0, 255, 0) if status else QtGui.QColor(255, 0, 0)

        name_item = QtGui.QTableWidgetItem(name)
        name_item.setBackgroundColor(back_color)
        self.tableWidget.setItem(new_row_index, 0, name_item)

        try:
            limit_item = QtGui.QTableWidgetItem(str(limit))
            limit_item.setBackgroundColor(back_color)
            self.tableWidget.setItem(new_row_index, 1, limit_item)
        except Exception, ex:
            limit_item = QtGui.QTableWidgetItem(limit)
            limit_item.setBackgroundColor(back_color)
            self.tableWidget.setItem(new_row_index, 1, limit_item)

        try:
            value_item = QtGui.QTableWidgetItem(str(value))
            value_item.setBackgroundColor(back_color)
            self.tableWidget.setItem(new_row_index, 2, value_item)
        except Exception,ex:
            value_item = QtGui.QTableWidgetItem(value)
            value_item.setBackgroundColor(back_color)
            self.tableWidget.setItem(new_row_index, 2, value_item)

        status_item = QtGui.QTableWidgetItem('PASS' if status else 'FAIL')
        status_item.setBackgroundColor(back_color)
        self.tableWidget.setItem(new_row_index, 3, status_item)

        mag_item = QtGui.QTableWidgetItem(msg)
        mag_item.setBackgroundColor(back_color)
        self.tableWidget.setItem(new_row_index, 4, mag_item)

    # 初始化信号处理
    def _init_event(self):
        self.btn_start.clicked.connect(self._start)
        # 自定义信号连接
        self.appendInfo.connect(self.__appendInfo)

    # textEdit信息更新
    # 1 默认颜色, 2 红色, 3=#00FFFF, 其它按默认色
    def __appendInfo(self, msg, color=1):
        if color is False or color == 2:
            self.txt_msg.append(u"""<HTML><font size="5" color="#FF0000">{0}:{1}</font> </HTML>""".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
        elif color == 3:
            self.txt_msg.append(u"""<HTML><font size="5" color="#00FFFF">{0}:{1}</font> </HTML>""".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
        else:
            self.txt_msg.append(u"""<HTML><font size="5" color="#00FF00">{0}:{1}</font> </HTML>""".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))

    # 写信息
    # 1 默认颜色, 2 红色, 3=#00FFFF, 其它按默认色
    def __appText(self, msg, color=1):
        self.appendInfo.emit(msg, color)

    # 开始检测
    def _start(self):
        self.produce_check.start()

    def _test_window(self, title, info):
        self.produce_check.question(title, info, r'.\\resource\\no_img.jpg', self)

    def _test_step_start(self, name):
        pass


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    trans = ProduceCheckWin()
    trans.show()
    sys.exit(app.exec_())