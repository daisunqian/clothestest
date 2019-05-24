# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\hely\he\Pyprojects\Jacquard_SRC\loginui.ui'
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
        Dialog.resize(563, 418)
        Dialog.setStyleSheet(_fromUtf8(""))
        self.lab_back = QtGui.QLabel(Dialog)
        self.lab_back.setGeometry(QtCore.QRect(10, 0, 621, 421))
        self.lab_back.setText(_fromUtf8(""))
        self.lab_back.setObjectName(_fromUtf8("lab_back"))
        self.txt_name = QtGui.QLineEdit(Dialog)
        self.txt_name.setGeometry(QtCore.QRect(180, 60, 301, 40))
        self.txt_name.setMinimumSize(QtCore.QSize(0, 40))
        self.txt_name.setObjectName(_fromUtf8("txt_name"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(80, 150, 91, 24))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.txt_pwd = QtGui.QLineEdit(Dialog)
        self.txt_pwd.setGeometry(QtCore.QRect(180, 140, 301, 40))
        self.txt_pwd.setMinimumSize(QtCore.QSize(0, 40))
        self.txt_pwd.setObjectName(_fromUtf8("txt_pwd"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(80, 60, 91, 24))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(70, 220, 108, 24))
        self.label.setObjectName(_fromUtf8("label"))
        self.cmb_testtype = QtGui.QComboBox(Dialog)
        self.cmb_testtype.setGeometry(QtCore.QRect(180, 220, 301, 30))
        self.cmb_testtype.setObjectName(_fromUtf8("cmb_testtype"))
        self.chk_debug = QtGui.QCheckBox(Dialog)
        self.chk_debug.setGeometry(QtCore.QRect(180, 280, 111, 28))
        self.chk_debug.setObjectName(_fromUtf8("chk_debug"))
        self.rdo_roll = QtGui.QRadioButton(Dialog)
        self.rdo_roll.setGeometry(QtCore.QRect(290, 280, 101, 28))
        self.rdo_roll.setObjectName(_fromUtf8("rdo_roll"))
        self.rdo_rec = QtGui.QRadioButton(Dialog)
        self.rdo_rec.setGeometry(QtCore.QRect(390, 280, 101, 28))
        self.rdo_rec.setObjectName(_fromUtf8("rdo_rec"))
        self.layoutWidget = QtGui.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(70, 340, 431, 62))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnOK = QtGui.QPushButton(self.layoutWidget)
        self.btnOK.setMinimumSize(QtCore.QSize(0, 60))
        self.btnOK.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btnOK.setObjectName(_fromUtf8("btnOK"))
        self.horizontalLayout.addWidget(self.btnOK)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_cancel = QtGui.QPushButton(self.layoutWidget)
        self.btn_cancel.setMinimumSize(QtCore.QSize(0, 60))
        self.btn_cancel.setMaximumSize(QtCore.QSize(16777215, 100))
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.horizontalLayout.addWidget(self.btn_cancel)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "login", None))
        self.label_2.setText(_translate("Dialog", "密  码：", None))
        self.label_3.setText(_translate("Dialog", "用户名：", None))
        self.label.setText(_translate("Dialog", "测试类型：", None))
        self.chk_debug.setText(_translate("Dialog", "debug", None))
        self.rdo_roll.setText(_translate("Dialog", "滚压", None))
        self.rdo_rec.setText(_translate("Dialog", "面压", None))
        self.btnOK.setText(_translate("Dialog", "确 定", None))
        self.btn_cancel.setText(_translate("Dialog", "取 消", None))

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    ui = Ui_Dialog()
    # ui.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
    ui.show()
    sys.exit(app.exec_())
