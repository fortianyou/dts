#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
日志模块, 支持 append 和 flush 操作
日志目录为项目根目录下的 log 文件夹
"""
import logging
import logging.handlers
import os
import time
try:
    import ujson as json
except ImportError:
    import json


__inited_loggers = {}
__all__ = ['get_logger']


class SmartLogger(logging.Logger):
    """添加了功能:
    支持将 key-value 内容输出成字符串
    """
    def __init__(self, name, level=logging.NOTSET):
        super(SmartLogger, self).__init__(name, level)

    def flush(self, level, pairs, *args, **kwargs):
        """以制定等级输出 key-value 中的数据

        参数:
            level: 日志等级, 字符串. 必须是 logging 支持的类型
                   注意: 这里可能带来安全问题
            pairs: 需要输出的数据对
        """
        # 黑名单包括:
        msg = json.dumps(pairs)
        if level == 'debug':
            if self.isEnabledFor(logging.DEBUG):
                self._log(logging.DEBUG, msg, args, **kwargs)
        elif level == 'info':
            if self.isEnabledFor(logging.INFO):
                self._log(logging.INFO, msg, args, **kwargs)
        elif level == 'warning':
            if self.isEnabledFor(logging.WARNING):
                self._log(logging.WARNING, msg, args, **kwargs)
        elif level == 'error':
            if self.isEnabledFor(logging.ERROR):
                self._log(logging.ERROR, msg, args, **kwargs)
        elif level == 'critical':
            if self.isEnabledFor(logging.CRITICAL):
                self._log(logging.CRITICAL, msg, args, **kwargs)
        else:
            raise ValueError('Invalid_log_level')


class MultiProcessingTimedRotatingFileHandler(
        logging.handlers.TimedRotatingFileHandler):
    """多进程日志切分的文件 Handler
    """

    def doRollover(self):
        """直接复制了 TimedRotatingFileHandler 中的函数, 修改了部分
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if not os.path.exists(dfn):
            os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
            # find the oldest log file and delete it
            for s in self.getFilesToDelete():
                os.remove(s)
        self.mode = 'a'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and \
                not self.utc:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                # DST kicks in before next rollover,
                # so we need to deduct an hour
                if not dstNow:
                    newRolloverAt = newRolloverAt - 3600
                # DST bows out before next rollover, so we need to add an hour
                else:
                    newRolloverAt = newRolloverAt + 3600
        self.rolloverAt = newRolloverAt


def __init_logger(logger_name, log_filename, logger_level, file_level=None):
    """初始化

    参数:
        logger_name: logger 的名字
        log_filename: 日志文件的路径
        logger_level: logger 的日志等级, 等级过低不会触发写日志操作
        file_level: 日志文件的日志等级, 等级太低不会出发写入文件操作
    """
    global __inited_loggers

    # formatter
    fmt = '%(levelname)s %(asctime)s %(filename)s|%(lineno)d\t%(message)s'
    formatter = logging.Formatter(fmt)

    # 日志 handler
    handler = MultiProcessingTimedRotatingFileHandler(
        log_filename,
        when='MIDNIGHT',
        interval=1,
        backupCount=0,
    )
    logger = None
    if logger_name == 'root':
        file_level = logging.WARNING
        logger = logging.getLogger()  # root logger of logging
    else:
        if file_level is None:
            file_level = logger_level
        logger = SmartLogger(logger_name, logger_level)

    # handler 等级
    handler.setLevel(file_level)
    # handler 格式
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logger_level)

    # 添加到工厂中
    if logger_name in __inited_loggers:
        del __inited_loggers[logger_name]
    __inited_loggers[logger_name] = logger


def get_logger(name):
    """工厂方式获取一个 logger

    参数:
        name: logger 的名字
    """
    global __inited_loggers

    # 不存在, 初始化一个
    if name not in __inited_loggers:
        # 固定日志位置为项目根目录下的 log 文件夹
        # 日志文件名为 {name}_log,  切分后为 {name}_log.YYYY-MM-DD
        log_dir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '../../../log',
        )
        # 判断文件夹是否存在
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        # 日志文件的路径
        log_path = os.path.join(
            log_dir,
            '{0}_log'.format(name),
        )
        __init_logger(name, log_path, logging.INFO)

    return __inited_loggers[name]

# 默认初始化 root logger
get_logger('root')
