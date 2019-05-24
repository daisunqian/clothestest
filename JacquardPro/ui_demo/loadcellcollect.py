# -*- coding:utf-8 -*-

from loadcellcollectui import Ui_Dialog
from PyQt4.QtGui import *
from PyQt4 import Qt
from PyQt4 import QtCore
import serial.tools.list_ports
from threading import Thread
import time
import datetime
from Comm.LoadCellData import LocalCell
from FixtureControl.APPConfigparse import APPConfigparse


class loadcellcollect(Ui_Dialog):

    def __init__(self, type, appconfig, localCell):
        super(loadcellcollect, self).__init__()
        self.loadcell_type = type
        self._port_init = True
        self._port_config_status = False  # 端口配置成功True
        self.appconfig = appconfig
        self.loadcell = localCell
        self._reading = False


        self._init_port()
        self._init_event()

    @property
    def port_config_status(self):
        return self._port_config_status

    # 初始化端口
    def _init_port(self):
        self._port_init = True
        port_list = list(serial.tools.list_ports.comports())
        for port_obj in port_list:
            self.comboBox.addItem(port_obj.device)

        # 设置当前显示项
        port = self.appconfig.loadcell_port
        index = self.comboBox.findText(port)
        if index >= 0:
            self.comboBox.setCurrentIndex(index)
        else:
            self.comboBox.setCurrentIndex(-1)

        self._port_init = False

    def _init_event(self):
        self.pushButton_2.clicked.connect(self._stop)
        self.pushButton.clicked.connect(self._start)
        self.comboBox.currentIndexChanged.connect(self._port_change)

    def _port_change(self, index):
        if self._port_init is False and index >= 0:
            self._port_config_status = False
            port = str(self.comboBox.currentText())

            if isinstance(self.loadcell, LocalCell):
                self.loadcell.CloseSerial()

            try:
                self.loadcell = LocalCell()
                self.loadcell.OpenSerial(port)
                self._port_config_status = True
                self._write_item('loadcell object init ok')

                if self.checkBox.isChecked():
                    if self.loadcell_type == 1:
                        self.appconfig.Rectangular_probe_Port = port
                    elif self.loadcell_type == 2:
                        self.appconfig.Roller_probe_Port = port
                    elif self.loadcell_type == 3:
                        self.appconfig.Vibrate_loadcell_port = port

            except Exception, ex:
                self._write_item('loadcell object init fail：' + ex.message)

    def _start(self):
        # print self.loadcell
        if isinstance(self.loadcell, LocalCell):
            self._reading = True
            self._write_item('collect start')
            th = Thread(target=self._start_collect)
            th.start()
        else:
            self._write_item('loadcell object not init')
            QMessageBox.warning(self, 'info', 'loadcell object not init')

    def _stop(self):
        self._reading = False
        self._write_item('collect stop')

    # 开始采集
    def _start_collect(self):
        try:
            while self._reading:
                read_data = self.loadcell.read_test()
                self._write_item(read_data)
                time.sleep(1)
        except Exception, ex:
            self._write_item('colect exception :' + ex.message)
            self._stop()

    # 写数据到UI
    def _write_item(self, datas):
        if datas is not None:
            item = QListWidgetItem("{0}:{1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(datas)))
            self.listWidget.addItem(item)
            self.listWidget.setCurrentItem(item)  # 设置为当前项


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = loadcellcollect(1, None, None)
    ui.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
    ui.show()
    sys.exit(app.exec_())