# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\hely\he\Pyprojects\Jacquard_SRC\AffirmWindowui.ui'
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
        Dialog.resize(681, 448)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(1, 2, 1, 2)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lab_img = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lab_img.sizePolicy().hasHeightForWidth())
        self.lab_img.setSizePolicy(sizePolicy)
        self.lab_img.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_img.setObjectName(_fromUtf8("lab_img"))
        self.gridLayout.addWidget(self.lab_img, 0, 0, 1, 2)
        self.line_2 = QtGui.QFrame(Dialog)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout.addWidget(self.line_2, 1, 0, 1, 2)
        self.txt_msg = QtGui.QTextEdit(Dialog)
        self.txt_msg.setStyleSheet(_fromUtf8("font: 75 12pt \"Arial\";"))
        self.txt_msg.setReadOnly(True)
        self.txt_msg.setObjectName(_fromUtf8("txt_msg"))
        self.gridLayout.addWidget(self.txt_msg, 2, 0, 1, 2)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 3, 0, 1, 2)
        self.btn_ok = QtGui.QPushButton(Dialog)
        self.btn_ok.setObjectName(_fromUtf8("btn_ok"))
        self.gridLayout.addWidget(self.btn_ok, 4, 0, 1, 1)
        self.btn_fail = QtGui.QPushButton(Dialog)
        self.btn_fail.setObjectName(_fromUtf8("btn_fail"))
        self.gridLayout.addWidget(self.btn_fail, 4, 1, 1, 1)
        self.gridLayout.setRowStretch(0, 4)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)
        self.gridLayout.setRowStretch(3, 1)
        self.gridLayout.setRowStretch(4, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Affirm", None))
        self.lab_img.setText(_translate("Dialog", "No img", None))
        self.txt_msg.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial\'; font-size:12pt; font-weight:72; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.btn_ok.setText(_translate("Dialog", "YES", None))
        self.btn_fail.setText(_translate("Dialog", "NO", None))


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    trans = Ui_Dialog()
    trans.show()
    sys.exit(app.exec_())

