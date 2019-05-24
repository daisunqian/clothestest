# -*- coding=utf-8 -*-


from ut import PLineui
from PyQt4.QtGui import QPainter, QApplication, QColor,QWidget
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import Qt,QRect


class PLWidget(QWidget):
    changedlinevalue = pyqtSignal()

    def __init__(self, value, parent=None):
        super(PLWidget, self).__init__(parent)
        if value > 0:
            value = value * -1
        self._value = value
        self.changedlinevalue.connect(self._changedlinevalue)

    def paintEvent(self, QPaintEvent):
        self.drawRectangles()

    def drawRectangles(self):
        gem = self.geometry()
        qp = QPainter()
        qp.begin(self)
        color = QColor(0, 0, 0)
        color.setNamedColor('#d4d4d4')
        qp.setPen(color)
        qp.setBrush(QColor(200, 0, 0))
        # print "drawRectangles=",self._value
        qp.drawRect(0, gem.height(), gem.width(), self._value)
        qp.end()

    def drawrect(self, gc):
        gem = self.geometry()
        value = gc * -0.4
        self._value = value
        self.changedlinevalue.emit()

    def _changedlinevalue(self):
        self.repaint()
        # self.update()


class PLineView(PLineui):
    changedlinevalue = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(PLineView, self).__init__(parent)
        self._line_widgets = {}
        self._init_line_widget()
        self.changedlinevalue.connect(self._changedlinevalue)

    def _init_line_widget(self):
        for index in range(12):
            self._line_widgets[index] = PLWidget(0)
            obj = "self.grid_lin{0}".format(index)
            eval(obj).addWidget(self._line_widgets[index], 0, 0)

    def update_line(self, datas):
        """
        刷新矩形图高度
        :param datas: 列表类型数据，元素是数字类型数据,必须有12个元素
        如 ls=[1,2,3,4,5,6,7,8,9,10,11,12]
        :return:
        """
        if datas is None and len(datas) != 12:
            return
        for data, index in zip(datas, range(0, len(datas))):
            self._line_widgets[index].drawrect(data)
            self.changedlinevalue.emit(index, data)

    def update_lines(self, datasource):
        """
        刷新矩形图高度
        :param datas: 列表类型数据，元素是列表类型，子列表元素是数字类型数据,必须有12个元素
        如:ls=[[1,2,3,4,5,6,7,8,9,10,11,12],[12,11,10,9,8,7,6,5,4,3,2,1]]
        :return:
        """
        if datasource is None and len(datasource) == 0:
            return
        for datas in datasource:
            if len(datas) < 12:
                continue
            self.update_line(datas)

    def _changedlinevalue(self,index, datas):
        obj = "self.lab_line{0}".format(index)
        eval(obj).setText("L{0}-{1}".format(index, datas))


def _th_test(win):
    import random,time
    from threading import Thread
    # self._MCUComm.init()
    # self._MCUComm.Start_T()
    # self._MCUComm.Start_T_Collect()
    time.sleep(0.3)
    # def th(mcu):
    def th():
        last_str = ''
        while True:
            # datastr = last_str + mcu.Read_Buff()
            # if len(datastr) == 0:
            #     time.sleep(0.01)
            #     continue
            # print datastr
            # last_str = ''
            # data_spls = datastr.split('\r\n')
            # for record in data_spls:
            #     if len(record) > 1:
            #         try:
            #             ls = [int(data1) for data1 in record.split(',')[1:]]  # 第1个是prox数据，从第二个开始
            #             if len(ls) == 12:
            #                 print "ls",ls
            #                 self.update_line(ls)
            #         except Exception, ex:
            #             pass
            #     else:
            #         last_str = record

            datas = []
            for index in range(12):
                datas.append(random.randint(0, 600))
            win.update_line(datas)
            time.sleep(0.05)

    # th_s = Thread(target=th, args=(self._MCUComm,))
    th_s = Thread(target=th)
    th_s.setDaemon(True)
    th_s.start()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = PLineView()
    win.show()
    _th_test(win)
    sys.exit(app.exec_())