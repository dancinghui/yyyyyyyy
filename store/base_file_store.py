#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from store.base_store import BaseStore
from util.file_util import CsvFile
from util.other_util import TimeUtil
import os
import ConfigParser


class BaseFileStore(BaseStore):
    def __init__(self, file_save_class=CsvFile):
        BaseStore.__init__(self)
        self.file_save_class=file_save_class

    def load_file_config(self, section):
        file_conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../conf/file_conf.ini")
        configParser = ConfigParser.ConfigParser()
        configParser.readfp(open(file_conf_path,'rb'))

        if configParser.has_option(section, "dir_name"):
            file_save_dir = configParser.get(section, "dir_name")
        else:
            file_save_dir = configParser.get("common", "dir_name")

        if not configParser.has_option(section, "file_name"):
            raise Exception("need file_name to create file_db which used to save data")

        file_save_name = configParser.get(section, "file_name")

        if '%s' in file_save_name:
            file_save_name = file_save_name % TimeUtil.get_today_time_str()
        else:
            file_save_name += "_%s" % TimeUtil.get_today_time_str()

        file_save_path = os.path.join(file_save_dir, file_save_name)

        self.file_save_path_exists = False
        if os.path.exists(file_save_path):
            self.file_save_path_exists = True

        self.file_save_path = file_save_path
        self.client = self.file_save_class(file_save_path, 'ab+')





