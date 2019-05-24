# -*- coding=utf-8 -*-

import logging
from logging import handlers


class Logger(object):
    # 日志级别关系映射
    level_relations ={
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    # 创建日志文件对象
    # filename：日志名称, level=日志级别
    # print_flag： True打印到屏幕,否则不打印,默认不打印
    # backupCount：备份文件的个数
    # when是间隔的时间单位，单位：S秒，M分，H小时，D天，W每星期（interval==0时代表星期一），midnight每天凌晨
    # fmt 输出格式(默认是：日期时间，写入信息)
    def __init__(self, filename, print_flag=False, level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(levelname)s: %(message)s'):
        # (未使用格式日期时间，执行路径， 行号，写入信息)
        # fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
        self.logger = logging.getLogger(filename)
        # 设置日志格式
        self.format_str = logging.Formatter(fmt)
        # 设置日志级别
        self.logger.setLevel(self.level_relations.get(level))
        # 往文件里写入 #指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        self.th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount, encoding='utf-8')

        # 设置文件里写入的格式
        self.th.setFormatter(self.format_str)
        # 把对象加到logger里
        self.logger.addHandler(self.th)

        # 往屏幕上输出
        self.sh = logging.StreamHandler()
        # 设置屏幕上显示的格式
        self.sh.setFormatter(self.format_str)

        if print_flag:
            # 把对象加到logger里
            self.logger.addHandler(self.sh)

    # 设置打印到屏幕状态
    # true打印，否则不打印
    def set_print(self, print_flag):
        if print_flag:
            # 把对象加到logger里
            self.logger.addHandler(self.sh)
        else:
            self.logger.removeHandler(self.sh)

    # 设置日志格式
    def set_formate(self, fmt='%(asctime)s - %(levelname)s: %(message)s'):
        self.format_str = logging.Formatter(fmt)
        # 设置文件里写入的格式
        self.th.setFormatter(self.format_str)
        # 设置屏幕上显示的格式
        self.sh.setFormatter(self.format_str)


if __name__ == '__main__':
    print Logger.level_relations
    log = Logger('all.log', print_flag=True, level='debug')
    log.logger.debug(u'debug')
    log.logger.info(u'info')
    log.logger.warning(u'警告')
    log.logger.error(u'报错')
    log.logger.critical(u'严重')
    Logger('error.log', level='error').logger.error('error')