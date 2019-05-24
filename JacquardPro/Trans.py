#coding=utf-8

import sys
from PyQt4 import QtGui, QtCore



try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class Trans(QtGui.QWidget):

    def __init__(self):
        super(Trans, self).__init__()
        self.initUI()
        self.resize(1589, 1091)
        # button = QtGui.QPushButton('Close', self)
        # self.connect(button, QtCore.SIGNAL('clicked()'), QtGui.qApp,QtCore.SLOT('quit()'))

        lab = QtGui.QLabel(self)
        lab.setStyleSheet(_fromUtf8("background-color:rgb(255,255,255);\n"
                                       "color:rgb(0,255,0)"))
        font = QtGui.QFont()
        font.setPointSize(100)
        lab.setFont(font)
        lab.resize(1589, 1091)
        lab.setText(u"PASS")
        lab.setAlignment(QtCore.Qt.AlignCenter)
        lab.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

    def initUI(self):
        # self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    trans = Trans()
    trans.show()
    sys.exit(app.exec_())