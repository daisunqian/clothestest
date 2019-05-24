# -*- coding:utf-8 -*-

from ui_demo.portsui import Ui_Dialog
from PyQt4 import QtCore, QtGui
import serial.tools.list_ports


class PortConfig(Ui_Dialog):
    def __init__(self, title):
        super(PortConfig, self).__init__()
        self.setWindowIcon(QtGui.QIcon('./resource/app.png'))
        self.currentport = ''
        self.currentbaudrate = 0
        self.label.setText(title)
        self._init_ports()
        self._init_baudrate()
        self.btnOK.clicked.connect(self._OK)
        self.btn_cancel.clicked.connect(self._Cancel)
        self.comboBox.currentIndexChanged.connect(self._port_indexchanged)
        self.comboBox_2.currentIndexChanged.connect(self._baudrate_indexchanged)

    def _init_ports(self):
        port_list = list(serial.tools.list_ports.comports())
        for port_obj in port_list:
            self.comboBox.addItem(port_obj.device)

        self.comboBox.setCurrentIndex(-1)

    def _init_baudrate(self):
        for baudrate in [1200, 4800, 9600, 19200, 38400, 115200]:
            self.comboBox_2.addItem(str(baudrate))

        self.comboBox_2.setCurrentIndex(-1)

    def _port_indexchanged(self, index):
        if index >= 0:
            self.currentport = self.comboBox.currentText()

    def _baudrate_indexchanged(self, index):
        if index >= 0:
            self.currentbaudrate = int(self.comboBox_2.currentText())

    def _OK(self):
        if len(self.currentport) == 0:
            QtGui.QMessageBox.warning(self, 'info', 'please select port')
            return
        if self.currentbaudrate == 0:
            QtGui.QMessageBox.warning(self, 'info', 'please select baudrate')
            return
        self.accept()

    def _Cancel(self):
            self.reject()


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    ui = PortConfig('port config')
    ui.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
    ui.show()
    sys.exit(app.exec_())