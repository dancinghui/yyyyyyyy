#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

import os
import re
import sys
import multiprocessing
from spiders.base.runtime import Log


def spider_run(spider):
    globals()['%s_instance' % spider].run()


class SpiderScanUtil(object):


    @staticmethod
    def _import_pkg(spidername, path, f):
        partions = path.split(os.sep)
        spiders_index = partions.index('spiders')
        pkg_name = '.'.join(partions[spiders_index:] + [f.split('.py')[0]])

        _import_str = 'from %s import %s' % (pkg_name, spidername)
        Log.info("do import pkg : %s" % _import_str)
        exec _import_str
        globals()[spidername] = locals()[spidername]

    @staticmethod
    def find_spider(path, f):
        if not f.endswith('.py'):
            return

        if f in ['__init__.py']:
            return

        file_name = os.path.join(path, f)
        with open(file_name, 'rb') as f1:
            content = f1.read()

        find = re.search('class ([A-Za-z_]+)\([^\s]+Spider', content)
        if find:
            spidername = find.group(1)
            SpiderScanUtil._import_pkg(spidername, path, f)
            return spidername

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


class ScheduleBase(object):
    spider_names = SpiderScanUtil.scan_spiders()

    def __init__(self, spider_thread_cnt=2):
        self.spider_thread_cnt = spider_thread_cnt

    def get_to_run_spiders(self):
        ret = dict()
        if not len(sys.argv[1:]):
            Log.info("[ + ] spiders can schedule: \n\n", "\n".join(list(ScheduleBase.spider_names)))
            return ret

        for p in sys.argv[1:]:

            p = p.split(':')
            t_cnt = self.spider_thread_cnt
            name = p[0]
            if len(p) == 2 and p[1].isdigit():
                t_cnt = int(p[1])

            if name not in ScheduleBase.spider_names:
                continue

            spider_instance = globals()[name](thread_cnt=t_cnt)
            ret[name] = spider_instance

        return ret

    def run(self):
        spiders = self.get_to_run_spiders()
        if len(spiders) == 0:
            Log.warning("[ - ] there is no spiders to run")
            return
        Log.info("================== spider list start=========================")
        for name, instance in spiders.items():
            globals()["%s_instance" % name] = instance
            Log.info(name)

        Log.info("================== spider list end ==========================")

        pool = multiprocessing.Pool(processes=len(spiders))
        for name, instance in spiders.items():
            pool.apply_async(spider_run, args=(name, ))
            Log.info("[ + ] spider started:  ", name)

        pool.close()
        pool.join()


def printUsage():
    print "[ + ] usage: %s [spider_name:thread_cnt]+" % sys.argv[0]
    print """[ + ] example:

            spider_schedule.py TuhuSpider:2 JdTuhuSpider:2
    """


if __name__ == '__main__':
    if len(sys.argv) < 2 or "-h" in sys.argv:
        printUsage()
    s = ScheduleBase(spider_thread_cnt=2)
    s.run()






