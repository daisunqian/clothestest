# -*- coding:utf-8 -*-

from PyQt4 import QtGui
from ui import Ui_MainWindow


class test(Ui_MainWindow):
    def __init__(self):
        super(test, self).__init__()
        # 状态栏初始化函数
        self.init_statusbar()
        #测试使用,写入文本至Label,测试长度过长的信息
        # self.label1.setText("label1".center(100,'*'))
        self.label1.setText("label1")
        self.label2.setText("label2")
        self.label3.setText("label3")
        self.label4.setText("label4")
        self.label5.setText("label5")
        self.label6.setText("label6")
        self.label7.setText("label7")
        self.label8.setText("label8")

    def init_statusbar(self):
        #隐藏TabWidget的第二个Tab,取消屏蔽可恢复
        self.camera2.deleteLater()
        # *********相邻Label设置固定的间隔？？？
        # self.label1.setAcceptDrops(True)
        # 创建label
        self.label1 = QtGui.QLabel()
        self.label2 = QtGui.QLabel()
        self.label3 = QtGui.QLabel()
        self.label4 = QtGui.QLabel()
        self.label5 = QtGui.QLabel()
        self.label6 = QtGui.QLabel()
        self.label7 = QtGui.QLabel()
        self.label8 = QtGui.QLabel()

        # 设置label的最小的宽度,为达到平铺设置为150，最小宽度可重设
        self.label1.setMinimumWidth(150)
        self.label2.setMinimumWidth(150)
        self.label3.setMinimumWidth(150)
        self.label4.setMinimumWidth(150)
        self.label5.setMinimumWidth(150)
        self.label6.setMinimumWidth(150)
        self.label7.setMinimumWidth(150)
        self.label8.setMinimumWidth(150)

        # 显示label中的内容至状态栏中
        self.statusbar.addWidget(self.label1)
        self.statusbar.addWidget(self.label2)
        self.statusbar.addWidget(self.label3)
        self.statusbar.addWidget(self.label4)
        self.statusbar.addWidget(self.label5)
        self.statusbar.addWidget(self.label6)
        self.statusbar.addWidget(self.label7)
        self.statusbar.addWidget(self.label8)


print '----1---',  __name__
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = test()
    ui.showMaximized()
    sys.exit(app.exec_())