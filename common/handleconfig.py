'''
***************
Name:Sunny
Time:2020/2/25
***************
'''
import os
from configparser import ConfigParser
from common.handlepath import conf_dir

class HandleConfig(ConfigParser):
    def __init__(self,conf_file):
        super().__init__()
        self.conf_file = conf_file
        self.read(conf_file)

    def write_conf(self,section,option,value):
        self.set(section=section,option=option,value=value)
        self.write(self.conf_file)

conf = HandleConfig(os.path.join(conf_dir,"config.ini"))
