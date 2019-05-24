# -*- coding:utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler
import sys,os

# 只用于测试


class AppLog(object):
    def __init__(self,logFile = None,logLevel=logging.DEBUG):
        #若未传参，默认文件名为logFile
        filename = os.path.join(os.getcwd(), "logs", "VIT.log") if logFile is None else logFile
        #创建log文件夹
        filedir = os.path.dirname(filename)
        print filedir
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        #logging模块的四大组件之一：Handler的用法
        formatter = logging.Formatter(
            '[%(asctime)s] -:- %(filename)s [Line:%(lineno)d : %(funcName)s] -:- [%(levelname)s] -:- %(message)s')
        # 每隔一天产生一个新的日志文件，最多生成30个日志文件，最老的将丢弃
        fileh = TimedRotatingFileHandler(filename, 'D', 1, 30)
        fileh.suffix = "%Y%m%d-%H%M.log"
        fileh.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)#*****
        self.logger.setLevel(logLevel)
        self.logger.addHandler(fileh)

# 利用python的module,创建单例模式
LOG_Instance = AppLog()