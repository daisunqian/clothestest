# -*- coding=utf-8 -*-

import time
from Comm.InnorevController import InnorevController


class IOControl(InnorevController):
    def __init__(self, port, baudrate=115200):
        super(IOControl, self).__init__(port, baudrate)

    # 读取output IO
    def get_output(self, index):
        return self.readSingle(index, inputType=1)

    # 读取input IO
    def get_input(self, index):
        return self.readSingle(index, inputType=0)

    # 写output IO
    def write_output(self, index, status, timeout=10):
        return self.writeDO(index, status, timeout)

    # index  inpurt索引
    # tovalue 是需要读到这个，tovalue=1
    # wait true循环读，直到到value的值返回
    # timeout 超时时间,单位秒（默认10秒）
    def _read_input(self, index, tovalue=1, wait=False, timeout=10):
        if timeout < 0:
            timeout = 0
        value = -1
        data = ''
        while timeout >= 0:
            value, data = self.get_input(index)
            if wait is True:
                if value == tovalue:
                    return value, data
                else:
                    timeout -= 1
                    time.sleep(1)  # 等待1秒
            else:
                return value, data
        return value, data

    # index  inpurt索引
    # tovalue 是需要读到这个，tovalue=1
    # wait true循环读，直到到value的值返回
    # timeout 超时时间,单位秒（默认10秒）
    def _read_output(self, index, tovalue=1, wait=False, timeout=10):
        if timeout < 0:
            timeout = 0
        value = -1
        data = ''
        while timeout >= 0:
            value, data = self.get_output(index)
            if wait is True:
                if value == tovalue:
                    return value, data
                else:
                    timeout -= 1
                    time.sleep(1)  # 等待1秒
            else:
                return value, data

        return value, data


if __name__ == '__main__':
    innorev = IOControl("COM8")

    print innorev.get_input(1)
    print innorev.get_output(2)
    print innorev.get_output(1)