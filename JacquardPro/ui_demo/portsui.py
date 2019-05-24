# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\hely\he\Pyprojects\Jacquard_SRC\portsui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(QtGui.QDialog):

    def __init__(self):
        super(Ui_Dialog, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(700, 474)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 30, 651, 61))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(100, 130, 108, 24))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(100, 240, 108, 24))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.comboBox = QtGui.QComboBox(Dialog)
        self.comboBox.setGeometry(QtCore.QRect(230, 130, 281, 30))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox_2 = QtGui.QComboBox(Dialog)
        self.comboBox_2.setGeometry(QtCore.QRect(230, 230, 291, 30))
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.layoutWidget = QtGui.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(100, 300, 501, 62))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btnOK= QtGui.QPushButton(self.layoutWidget)
        self.btnOK.setMinimumSize(QtCore.QSize(0, 60))
        self.btnOK.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btnOK.setObjectName(_fromUtf8("btnOK"))
        self.horizontalLayout_2.addWidget(self.btnOK)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btn_cancel = QtGui.QPushButton(self.layoutWidget)
        self.btn_cancel.setMinimumSize(QtCore.QSize(0, 60))
        self.btn_cancel.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.horizontalLayout_2.addWidget(self.btn_cancel)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "port cinfig", None))
        self.label.setText(_translate("Dialog", "端口配置", None))
        self.label_2.setText(_translate("Dialog", "端 口:", None))
        self.label_3.setText(_translate("Dialog", "波特率", None))
        self.btnOK.setText(_translate("Dialog", "确 定", None))
        self.btn_cancel.setText(_translate("Dialog", "取 消", None))

