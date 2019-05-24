# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\hely\he\Pyprojects\Jacquard_SRC\JacquardPro\login_iqc.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(733, 463)
        self.rdo_iqc = QtGui.QRadioButton(Dialog)
        self.rdo_iqc.setGeometry(QtCore.QRect(180, 110, 271, 61))
        self.rdo_iqc.setStyleSheet(_fromUtf8("font: 12pt;"))
        self.rdo_iqc.setChecked(True)
        self.rdo_iqc.setObjectName(_fromUtf8("rdo_iqc"))
        self.rdo_ipqc = QtGui.QRadioButton(Dialog)
        self.rdo_ipqc.setGeometry(QtCore.QRect(180, 200, 311, 28))
        self.rdo_ipqc.setStyleSheet(_fromUtf8("font: 12pt;"))
        self.rdo_ipqc.setObjectName(_fromUtf8("rdo_ipqc"))
        self.btn_ok = QtGui.QPushButton(Dialog)
        self.btn_ok.setGeometry(QtCore.QRect(90, 370, 150, 46))
        self.btn_ok.setObjectName(_fromUtf8("btn_ok"))
        self.btn_cancel = QtGui.QPushButton(Dialog)
        self.btn_cancel.setGeometry(QtCore.QRect(400, 370, 150, 46))
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.rdo_oqc = QtGui.QRadioButton(Dialog)
        self.rdo_oqc.setGeometry(QtCore.QRect(180, 280, 311, 28))
        self.rdo_oqc.setStyleSheet(_fromUtf8("font: 12pt;"))
        self.rdo_oqc.setObjectName(_fromUtf8("rdo_oqc"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "测试类型选择", None))
        self.rdo_iqc.setText(_translate("Dialog", "   IQC测试", None))
        self.rdo_ipqc.setText(_translate("Dialog", "   IPQC测试", None))
        self.btn_ok.setText(_translate("Dialog", "确 定", None))
        self.btn_cancel.setText(_translate("Dialog", "取 消", None))
        self.rdo_oqc.setText(_translate("Dialog", "   OQC测试", None))

