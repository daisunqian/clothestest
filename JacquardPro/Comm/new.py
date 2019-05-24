#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   sqdai
@Contact :   654251408@qq.com
@Software:   PyCharm
@File    :   new.py
@Time    :   2019/4/23 11:13

'''

# -*- coding=utf-8 -*-

from newui import Ui_Dialog
from PyQt4 import QtGui, QtCore
import os
from Comm.picture import Pictures
from FixtureControl import APPConfigparse

class New(Ui_Dialog):
    # 超时时间,单位秒
    WAIT_TIME_OUT = 10

    def __init__(self,timer=True, parent=None,):
        super(New, self).__init__(parent)
        self.pushButton.clicked.connect(self._result_ok)
        self.pushButton_2.clicked.connect(self._result_fail)

        # self.apptimer = QtCore.QTimer()
        # self.apptimer.timeout.connect(self._timer_out)
        # if timer:
        #     self.apptimer.start(1000)
        # self._timeout = New.WAIT_TIME_OUT
        Pictures.getpicture(os.getcwd() + "\\resource")
    # 设置计时器使用状态
    def setTimer(self, on):
        if on:
            self.apptimer.start(1000)
        else:
            self.apptimer.stop()

    # 间隔时间到
    def _timer_out(self):
        self._timeout -= 1
        #self.lineEdit.setText('no({0}s)'.format(self._timeout))
        self.pushButton_2.setText('no({0}s)'.format(self._timeout))
        # 时间到，失败错误退出
        if self._timeout == 0:
            self.reject()
            self.apptimer.stop()
            # self.accept()

    def _result_ok(self):
        self.accept()

    def _result_fail(self):
        self.reject()

    # 按键释放信号
    def keyReleaseEvent(self, *args, **kwargs):
        # print args, kwargs
        event = args[0]
        if isinstance(event, QtGui.QKeyEvent):
            # print 'current=', event.key()
            # if event.key() == QtCore.Qt.Key_Return:
            #     self._result_ok()
            if event.key() == QtCore.Qt.Key_Right:
                self.btn_fail.setFocus()
            elif event.key() == QtCore.Qt.Key_Left:
                self.btn_ok.setFocus()
            elif event.key() == QtCore.Qt.Key_N:
                self._result_fail()
            elif event.key() == QtCore.Qt.Key_Y:
                self._result_ok()


    # 左侧显示信息
    def set_display(self, info):
        self.txt_msg.append(info)


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    trans = New(timer=True)
    trans.show()
    sys.exit(app.exec_())