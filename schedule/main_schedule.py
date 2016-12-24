#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from schedule.exporter_schedule import ExporterSchedule
from schedule.spider_schedule import SpiderSchedule

usage = """
  Usage : python main_schedule.py -s spider:thread_cnt -e export:thread_cnt:clz_param

          example:
                python main_schedule.py -s JdTuhuSpider:1 -e TyreExport:1:{\\"query\\":{\\"source\\":\\"qccr\\"}}
"""

print usage

export_shedule = ExporterSchedule()
export_shedule.run()

spider_schedule = SpiderSchedule()
spider_schedule.run()