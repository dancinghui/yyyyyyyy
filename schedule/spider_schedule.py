#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

import os
import re
import sys
import multiprocessing
from spiders.base.runtime import Log
from schedule.base import ScanUtil, BaseSchedule


def spider_run(spider):
    globals()['%s_instance' % spider].run()


class SpiderScanUtil(ScanUtil):

    @staticmethod
    def find_spider(path, f):
        return ScanUtil.find_pattern(path, f, 'class ([A-Za-z_]+)\([^\s]+Spider')

    @staticmethod
    def scan_spiders():
        ret = set()
        spiders_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../spiders')
        for path, ds, fs in os.walk(spiders_dir):
            for f in fs:
                name = SpiderScanUtil.find_spider(path, f)
                if not name:
                    continue
                ret.add(name)

        return ret


class SpiderSchedule(BaseSchedule):
    spider_names = SpiderScanUtil.scan_spiders()

    def __init__(self, thread_cnt=2):
        BaseSchedule.__init__(self, "spider", thread_cnt=thread_cnt)
        self.all_runners = SpiderSchedule.spider_names

    def get_runners(self):
        return self.parse_param('-s')



def printUsage():
    print "[ + ] usage: %s [spider_name:thread_cnt]+" % sys.argv[0]
    print """[ + ] example:

            spider_schedule.py TuhuSpider:2 JdTuhuSpider:2
    """








