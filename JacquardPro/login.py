# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.Qt import Qt
from PyQt4.QtCore import QRegExp
from ui_demo.loginui import Ui_Dialog
from FixtureControl import APPConfigparse
from Comm import MD5
from Comm.picture import Pictures
import os

class Login(Ui_Dialog):

    def __init__(self, file_name):
        super(Login, self).__init__()
        Pictures.getpicture(os.getcwd() + "\\resource")
        self.setWindowIcon(QIcon(Pictures.appfilename))
        #self.appconfg = APPConfigparse.APPConfigparse('./config.ini')
        config_name = file_name
        self.appconfg = APPConfigparse.APPConfigparse(config_name)
        self.txt_name.setText(self.appconfg.UserName)
        print Pictures.backfilename
        background = QPixmap(Pictures.backfilename)
        background = background.scaled(self.lab_back.width(), self.lab_back.width())
        self._init_ui()
        self.lab_back.setPixmap(background)
        self.txt_pwd.setEchoMode(QLineEdit.Password)
        self.txt_pwd.setMaxLength(8)
        self.txt_pwd.setContextMenuPolicy(Qt.NoContextMenu)  # 这个语句设置QLineEdit对象的上下文菜单的策略。复制，粘贴，。。。，是否可用
        self.txt_pwd.setPlaceholderText(u"密码不超8位数字和字母组成")  # 只要行编辑为空，设置此属性将使行编辑显示为灰色的占位符文本。默认情况下，此属性包含一个空字符串。这是非常
        # regx = QRegExp("^[a-zA-Z][0-9A-Za-z]{8}")  # 为给定的模式字符串构造一个正则表达式对象。
        regx = QRegExp("^[0-9][0-9A-Za-z]{8}")  # 为给定的模式字符串构造一个正则表达式对象。
        validator = QRegExpValidator(regx, self.txt_pwd)  # 构造一个验证器
        self.txt_pwd.setValidator(validator)  # 数据输入验证器
        self.btnOK.clicked.connect(self._btnok)
        self.btn_cancel.clicked.connect(self._btncancel)
        self.chk_debug.clicked.connect(self._chk_debug_click)

    def _init_ui(self):
        self.cmb_testtype.setEnabled(False)
        self.rdo_roll.setEnabled(False)
        self.rdo_rec.setEnabled(False)
        self.cmb_testtype.addItems(APPConfigparse.TEST_TYPE_Names)
        test_type = self.appconfg.Test_type
        if self.appconfg.Test_mode == 1:
            self.rdo_roll.setChecked(True)
        else:
            self.rdo_rec.setChecked(True)
        self.chk_debug.setChecked(self.appconfg.Debug)
        if APPConfigparse.TEST_TYPE.has_key(test_type):
            self.cmb_testtype.setEditText(test_type)
        else:
            QMessageBox.information(self, u'提示', u'测试类型配置不正确')

    def _to_testtype(self, type_item):
        if type_item == '成品衣服测试':
            pass

    def _btnok(self):
        if len(self.txt_name.text()) == 0:
            QMessageBox.warning(self, 'info', 'please input name')
            return
        if len(self.txt_pwd.text()) == 0:
            QMessageBox.warning(self, 'info', 'please input password')
            return
        in_pwd = self.txt_pwd.text()
        pwd = MD5.tomd5(str(in_pwd))
        # print pwd
        if pwd == self.appconfg.Login_pwd:
            self.appconfg.UserName = self.txt_name.text()
            self.accept()
        else:
            QMessageBox.warning(self, 'inf', 'Incorrect password')

    def _btncancel(self):
        self.reject()

    def _chk_debug_click(self):
        self.appconfg.Debug = self.chk_debug.isChecked()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = Login(sys.argv[1])
    # ui.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
    ui.show()
    sys.exit(app.exec_())