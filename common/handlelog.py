'''
***************
Name:Sunny
Time:2020/2/25
***************
'''
import logging
import os
from common.handleconfig import conf
from common.handlepath import logs_dir


class HandleLong(object):

    @staticmethod
    def logfile():
        # 创建一个日志收集器对象
        mylog = logging.getLogger(conf.get("log", "name"))
        # 设置日志收集器的收集等级
        mylog.setLevel("DEBUG")
        # 设置日志输出渠道
        # 控制台输出
        # 创建一个日志输出渠道对象
        sh = logging.StreamHandler()
        # 设置输出渠道的输出等级
        sh.setLevel("INFO")
        # 将日志输出渠道添加到日志收集器中
        mylog.addHandler(sh)

        # 日志文件输出
        # 创建一个日志文件输出渠道
        fh = logging.FileHandler(os.path.join(logs_dir, "Sunny.log"), encoding="utf8")
        # 设置日志输出渠道的输出等级
        fh.setLevel("INFO")
        # 将日志输出渠道添加到日志收集器中
        mylog.addHandler(fh)
        # 设置日志输出格式
        form = "%(asctime)s - [%(filename)s-->line:%(lineno)d] - %(levelname)s: %(message)s"
        # 创建一个日志输出格式对象
        fm = logging.Formatter(form)
        # 将日志输出渠道和日志格式绑定
        sh.setFormatter(fm)
        fh.setFormatter(fm)

        return mylog

log = HandleLong.logfile()
