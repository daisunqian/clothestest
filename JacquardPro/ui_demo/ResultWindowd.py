# -*- coding:utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore



try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

YELLOW_background = _fromUtf8("background-color:rgb(255,255,0);\n"
                                       "color:rgb(0,0,0)")

RED_background = _fromUtf8("background-color:rgb(255,0,0);\n"
                                       "color:rgb(255,0,0)")

GREEN_background = _fromUtf8("background-color:rgb(0,255,0);\n"
                                       "color:rgb(0,0,0)")

BLUE__background = _fromUtf8("background-color:rgb(0,0,0);\n"
                                       "color:rgb(0,0,255)")


class ResultWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ResultWindow, self).__init__(parent)
        self._initUI()
        self.resize(600, 600)
        # self.setWindowOpacity(0.5)
        self.display_lab = QtGui.QLabel(self)
        font = QtGui.QFont()
        font.setWeight(20)
        font.setPointSize(200)
        self.display_lab.setFont(font)
        self.display_lab.resize(600, 600)
        self.display_lab.setAlignment(QtCore.Qt.AlignCenter)
        self.display_lab.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        # self._center()

    def _center(self):  # 实现窗体在屏幕中央
        screen = QtGui.QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
        size = self.geometry()  # 同上
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)  # 调用move移动到指定位置

    def _initUI(self):
        # self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.SubWindow)

    def _fail_result(self):
        self.display_lab.setText(u"FAIL")
        self.display_lab.setStyleSheet(RED_background)

    def _pass_result(self):
        self.display_lab.setText(u"PASS")
        self.display_lab.setStyleSheet(BLUE__background)

    def _idle_result(self, value=u'IDLE'):
        self.display_lab.setText(value)
        self.display_lab.setStyleSheet(YELLOW_background)

    # 设置宽度
    def setwidth(self, wide=600, height=600):
        self.resize(wide, height)
        self.display_lab.resize(wide, height)

    # 设置显示
    def setResult(self, status):
        if isinstance(status, bool):
            if status:
                self._pass_result()
            else:
                self._fail_result()
        elif isinstance(status, str):
            up_rst = status.upper()
            if 'Y' == up_rst or 'OK' == up_rst or 'PASS' == up_rst:
                self._pass_result()
            else:
                self._fail_result()
        else:
            self._idle_result(str(status))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    trans = ResultWindow()
    trans.setResult(False)
    trans.show()
    sys.exit(app.exec_())