#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base_spider import BaseSpider
from parsers.tuhu import TuhuParse


class TuhuGlobleData(object):
    widths = {"145", "155", "165", "175", "185", "195", "196",
              "205", "210", "215", "225", "235", "245", "255", "265", "275",
              "285", "295", "30", "305", "30X", "30x9.5", "31", "315", "31X",
              "31x10.5", "325", "32X", "32x11.5", "33", "335", "33X",
              "33x12.5", "35", "37X", "55", "650", "700"}

    rats = {"9.5", "10.5", "11.5", "12.5", "16", "25", "30",
            "35", "40", "45", "50", "50Z", "55", "55Z", "60", "65", "70",
            "75", "80", "85", "105", "790"}

    rims = {"11", "12", "12C", "13", "13C", "13LT", "14", "14C",
            "15", "15C", "16", "16.5", "16C", "17", "18", "19", "20", "21",
            "22", "23", "24", "26", "28", "45", "540", "V"}


class TuhuSpider(BaseSpider):

    def __init__(self, queue_size=200, thread_cnt=10):
        BaseSpider.__init__(self, 'tuhuSpider', queue_size, thread_cnt)
        self.parser = TuhuParse(self)

    def genUrl(self, job):
        url = "http://item.tuhu.cn/List/Tires/%s/CP_Tire_AspectRatio=%s&CP_Tire_Rim=%s" \
              "&CP_Tire_Width=%s.html#ProductFilter" % (job.get('page'), job.get('rat'),
                                                        job.get('rim'), job.get('width'))

        return url

    def dispatcher(self, q):
        for width in TuhuGlobleData.widths:
            for rat in TuhuGlobleData.rats:
                for rim in TuhuGlobleData.rims:
                    d = {'width': width, 'rat': rat, 'rim': rim}
                    # d = {'width':215, 'rat':45, 'rim': 17}
                    print d
                    self.add_main_job(d)

    def run_job(self, job):
        if not job or not isinstance(job, dict):
            return

        if 'page' not in job:
            job.update({'page':str(1)})
        url = self.genUrl(job)
        resp = self.with_sleep_requests(url, sleep=1)
        if resp:
            items = self.parser.parse(resp.text, job)
            self.saveItems(items)


if __name__ == '__main__':
    t = TuhuSpider(thread_cnt=2)
    t.run()