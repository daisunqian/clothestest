# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\hely\he\Pyprojects\Jacquard_SRC\ProduceCheckui.ui'
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


class Ui_Form(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Ui_Form, self).__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)

    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(1147, 745)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setContentsMargins(1, 2, 1, 1)
        self.gridLayout.setSpacing(1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btn_start = QtGui.QPushButton(Form)
        self.btn_start.setObjectName(_fromUtf8("btn_start"))
        self.gridLayout.addWidget(self.btn_start, 0, 0, 1, 1)
        self.tableWidget = QtGui.QTableWidget(Form)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)
        self.txt_msg = QtGui.QTextEdit(Form)
        self.txt_msg.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 0);\n"
"color: rgb(0, 255, 0);"))
        self.txt_msg.setObjectName(_fromUtf8("txt_msg"))
        self.gridLayout.addWidget(self.txt_msg, 2, 0, 1, 1)
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 3)
        self.gridLayout.setRowStretch(2, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.btn_start.setText(_translate("Form", "开始", None))


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    trans = Ui_Form()
    trans.show()
    sys.exit(app.exec_())