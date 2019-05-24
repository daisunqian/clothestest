# -*- coding=utf-8 -*-

import time
from PyQt4.QtCore import pyqtSignal, QThread
from Comm.Logger import Logger
from Comm.AffirmWindow import AffirmWindow
from Comm.IndicationWindow import IndicationWindow
from Comm.new import New
import datetime


START_SIGNAL = 1
RESET_SIGNAL = 2
E_STOP_SIGNAL = 3


# jacquard 测试接口
class IJacquardTest(QThread):
    # 初始化通讯对象结束后接触
    # 参数，初始化信息
    connected_finished = pyqtSignal(list)
    # start信号到位和复位信号以及急停信号
    # 参数(信号类型：1->startbutton到位，2-> 复位信号产生, 3->急停信号产生)
    signal_happen = pyqtSignal(int)
    # 测试开始信号
    test_start = pyqtSignal()
    # 测试结束信号
    # 参数(sn, 测试结果true-pass,false-fail)
    test_end = pyqtSignal(str, bool)
    # 采集sn完成，返回sn
    read_sn = pyqtSignal(str)
    # 测试项开始测试信号
    # 参数(名称)
    item_start = pyqtSignal(str)
    # 测试项测试结束信号
    # (名称, 状态, 数据, 测试信息, 门限值)
    item_end = pyqtSignal(str, bool, str, str, str)
    # 信息显示信号
    # (信息，状态)
    display_msg = pyqtSignal(str, bool)
    # 通知调用打开UI
    # 参数: 标题, 提示信息
    manual_window = pyqtSignal(str, str)
    manual_window2 = pyqtSignal(str, str)
    touch_rowcount_diffenrence = pyqtSignal(str)
    touch_diffenrence = pyqtSignal(str)

    def __init__(self):
        super(IJacquardTest, self).__init__()
        self._manual_result = False          # 测试打开窗口结果, True成功，False失败
        self._manual_window_close = False    # True表示窗口关闭返回,否则还在打开状态
        self.current_item = ''               # 当前正在测试的测试项名称
        self._check_io_signal=False          # 检测io信号
        self._testing = False                # true测试中，否则处于空闲状态
        self._monitor = False                # start button监视，true正在监视，否则未监视
        self.current_sn = ''                 # 当前测试sn
        self.logger = None
        self.summary_dir = ''                #summary 文件路径
        self.start_time = datetime.datetime.now()           # 测试开始时间
        self.end_time = datetime.datetime.now()              # 测试结束时间
        self.current_test_result = False                    # 当前测试结论,True测试成功，否则失败

    def _on_touch_diffenrence(self, differences):
        self.touch_diffenrence.emit(differences)

    def _on_touch_rawcount_diffenrence(self, rawcount_differences):
        self.touch_rowcount_diffenrence.emit(rawcount_differences)

    # 初始化对象,检测连接
    # auto = True自定查找端口
    # auto = True时，port_list端口集合有效
    def check_connect(self, auto=False, port_list=None):
        raise NotImplementedError()

    # 线程执行，启动信号监视
    def run(self):
        self._monitor = True
        self._reset_happen_time = time.time()
        while self._monitor:
            self.check_signal()

    # 获取summary文件路径
    # 返回当前配置路径summary_dir + current_sn组合的路径
    def get_save_dir(self, test_time = True):
        import os
        _dir = self.summary_dir
        if len(self.current_sn) > 0:
            _dir += "\\" + self.current_sn
        if test_time:
            _dir += "\\" + self.start_time.strftime("%Y%m%d%H%M%S")
        if os.path.exists(_dir) is False:
            os.makedirs(_dir)
        return _dir

    # 获取summary文件
    def get_summary_file(self):
        import os
        _dir = self.summary_dir
        if os.path.exists(_dir) is False:
            os.makedirs(_dir)
        file_path = _dir + "\\" + self.start_time.strftime("%Y%m%d") + ".csv"
        return file_path

    # 获取信号监视状态
    # true正在监控，否则未监控
    def get_monitor(self):
        return self._monitor

    # 获取测试状态,true正在测试，否则空闲
    def get_testing(self):
        return self._testing

    # 检测设备信号
    def check_signal(self):
        raise NotImplementedError()

    # 检测治具是否准备好
    def check_Fixture(self):
        raise NotImplementedError()

    # 启动测试
    def start_test(self):
        raise NotImplementedError()

    # 停止测试
    def stop_test(self):
        self._testing = False
        self.test_end.emit(self.current_sn, False)

    # 设备回原点
    def backhome(self):
        pass

    # 复位
    def reset(self):
        raise NotImplementedError()

    def open_new_window(self,):
        self._manual_window_close = False
        win = New()
        # win.set_display(title + "\n" + info)
        win.exec_()
        self._manual_window_close = True
        self._manual_result = win.result()
        return self._manual_result
    # 打开测试窗口
    def open_manual_window(self, title, info, img=None, parent=None):
        self._manual_window_close = False
        win = AffirmWindow(parent)
        win.setimg(img)
        win.set_display(title + "\n" + info)
        win.exec_()
        self._manual_window_close = True
        self._manual_result = win.result()
        return self._manual_result

#打开通知窗口
    def open_Indication_window(self,title, info, img=None, parent=None):
        self._manual_window_close = False
        win = IndicationWindow(parent)
        win.setimg(img)
        win.set_display(title + "\n" + info)
        win.exec_()
        self._manual_window_close = True
        self._manual_result = win.result()
        return self._manual_result


    # 通知主需要打开窗口
    def _on_manual_window(self,title, info,):
        self._manual_result = False
        self.manual_window.emit(title, info,)
        self._manual_window_close = False
        while self._manual_window_close is False:
            time.sleep(1)
        return self._manual_result

    def _on_manual_window2(self, title, info):
        self._manual_result = False
        self.manual_window2.emit(title, info)
        self._manual_window_close = False
        while self._manual_window_close is False:
            time.sleep(1)
        return self._manual_result

    # 创建日志对象
    # print_flag=True打印到控制台
    def _createLogger(self, filename=None, print_flag=False, level='debug'):
        import datetime
        if filename is None or len(filename) == 0:
            import os
            log_dir = r'.\\logs'
            if os.path.exists(log_dir) is False:
                os.mkdir(log_dir)
            filename = "{0}\{1}.log".format(log_dir, datetime.datetime.now().strftime('%Y%m%d'))
        return Logger(filename, print_flag=print_flag, level=level)

    # 触发连接完成信号
    def _on_connected_finished(self, init_list):
        self.connected_finished.emit(init_list)

    # 触发相应信号产生信号
    def _on_signal_happen(self, signal):
        self.signal_happen.emit(signal)

    # 触发测试开始信号
    def _on_test_start(self):
        self.test_start.emit()

    # 触发结束信号
    def _on_test_end(self, sn, status):
        self.test_end.emit(sn, status)

    #  触发采集到sn数据信号
    def _on_read_sn(self, sn):
        self.read_sn.emit(sn)

    # 触发测试项开始测试信号
    # 参数：名称
    def _on_item_start(self, name):
        self.item_start.emit(name)

    # 触发测试项测试结束信号
    # (名称, 状态, 数据, 测试信息)
    def _on_item_end(self, name, status, value, msg, limit='No'):
        self.item_end.emit(name, status, value, msg, limit)

    # 触发信息信号
    # 参数:方法名称，其它信息，状态, 所在文件名称,行号
    # 所在文件名称=None表示自动读取,行号=None表示自动读取,否则使用传递数据
    def _on_display_msg(self, method, msg, status=False, filename=None, line_no=None):
        import datetime
        import sys

        pro_frame = sys._getframe().f_back
        # 获取代码调用函数行号
        if line_no is None:
            line_no = pro_frame.f_lineno
        # 获取文件名称
        if filename is None or len(filename) == 0:
            ls = pro_frame.f_code.co_filename.split('/')
            if len(ls) == 1:
                ls = pro_frame.f_code.co_filename.split('\\')
            filename = ls[-1]

        other_str = msg
        if isinstance(msg, unicode):
            other_str = msg.decode('utf-8')

        msg = str(datetime.datetime.now())
        msg += '-' + "filename:{0}".format(filename)
        msg += '-' + "method:{0}".format(method)
        msg += '-' + "[line:{0}]".format(line_no)
        msg += '- msg:' + other_str
        msg += "- [status:{0}]".format(status)
        # msg = "{0} -{1} -{2} -{3} -{4} -{5}".format(datetime.datetime.now(),
        #                                             "filename:{0}".format(filename),
        #                                             "method:{0}".format(method),
        #                                             "[line:{0}]".format(line_no),
        #                                             "message:{0}".format(other_str),
        #                                             "[status:{0}]".format(status))
        self.display_msg.emit(msg, status)
        if self.logger is None:
            self.logger = self._createLogger()
        if status:
            self.logger.logger.info(msg)
        else:
            self.logger.logger.error(msg)