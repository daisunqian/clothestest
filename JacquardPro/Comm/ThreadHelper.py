# -*- coding:utf-8 -*-
from threading import Thread
import inspect
import ctypes
import time

TIMEOUT = 100    # 超时时间，单位秒


# 强制退出线程
def stop_thread(thread):
    try:
        if isinstance(thread, Thread):
            _async_raise(thread.ident, SystemExit)
            start_time = time.time()
            try_st = time.time()
            while thread.is_alive():
                time.sleep(0.1)
                if time.time() - try_st >= 1:
                    _async_raise(thread.ident, SystemExit)
                    try_st = time.time()

                if time.time() - start_time > TIMEOUT:
                    break

            if thread.is_alive():
                _async_raise(thread.ident, SystemExit)

        return thread.is_alive() is False, 'stop' if thread.is_alive() is False else 'is alive'
    except Exception, ex:
        return False, ex.message



# 退出线程
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    # print 'res',res
    if res == 0:
        # print '"invalid thread id"'
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        # print 'PyThreadState_SetAsyncExc failed'
        raise SystemError("PyThreadState_SetAsyncExc failed")