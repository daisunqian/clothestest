# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '12345.ui'
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
    def __init__(self, parent=None):
        super(Ui_Dialog, self).__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(900, 600)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Agency FB"))
        font.setPointSize(14)


        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(0, 0, 900, 300))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.lineEdit.setText(u'请观察待测物品是否振动?')
        self.lineEdit.setFont(font)
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(0, 300, 450, 300))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton.setStyleSheet(_fromUtf8("background-color : rgb(0, 255, 0);"))
        self.pushButton.setFont(font)
        self.pushButton_2 = QtGui.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(450, 300, 450, 300))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.pushButton_2.setStyleSheet(_fromUtf8("background-color : rgb(255, 0, 0);"))
        self.pushButton_2.setFont(font)
        self.line = QtGui.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(0, 300, 900, 5))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.pushButton.setText(_translate("Dialog", "yes", None))
        self.pushButton_2.setText(_translate("Dialog", "no", None))

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    trans = Ui_Dialog()
    trans.show()
    sys.exit(app.exec_())
