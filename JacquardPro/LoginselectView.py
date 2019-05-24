# -*- coding: utf-8 -*-

from loginselectui import Loginselectui


class LoginselectView(Loginselectui):
    def __init__(self):
        super(LoginselectView, self).__init__()
        self.btn_ok.clicked.connect(self._ok)
        self.btn_cancel.clicked.connect(self._cancel)

    @property
    def iqc_test(self):
        return self.rdo_iqc.isChecked()

    @property
    def ipqc_test(self):
        return self.rdo_ipqc.isChecked()

    @property
    def oqc_test(self):
        return self.rdo_oqc.isChecked()

    def _ok(self):
        self.accept()

    def _cancel(self):
        self.reject()

