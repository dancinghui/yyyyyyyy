#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from schedule.base import ScanUtil,BaseSchedule
from spiders.base.runtime import Log
import os
import sys
import json


class ExporterScanUtil(ScanUtil):

    @staticmethod
    def find_exporter(path, f):
        return ScanUtil.find_pattern(path, f, 'class ([A-Za-z_]+)\([^\s]+Export')

    @staticmethod
    def scan_exporters():
        ret = set()
        spiders_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exporters')
        for path, ds, fs in os.walk(spiders_dir):
            for f in fs:
                name = ExporterScanUtil.find_exporter(path, f)
                if not name:
                    continue
                ret.add(name)

        return ret


class ExporterSchedule(BaseSchedule):
    exporter_names = ExporterScanUtil.scan_exporters()

    def __init__(self, thread_cnt=1):
        BaseSchedule.__init__(self, "exporter", thread_cnt=thread_cnt)
        self.all_runners = ExporterSchedule.exporter_names

    def get_runners(self):
        return self.parse_param('-e')





