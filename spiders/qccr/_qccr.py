#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base_spider import BaseSpider
from parsers.qccr import QccrParser


class QccrDATA(object):
    p = [
        ['0','199'],
        ['200', '499'],
        ['500', '799'],
        ['800', '999'],
        ['1000', '1499'],
        ['1500', '1999'],
        ['2000', '']
    ]

    url_template = 'http://www.qccr.com/list_lt/sub_p%s~%s_c%d_s25/'


class QccrSpider(BaseSpider):
    def __init__(self, thread_cnt=10, queue_size=200):
        BaseSpider.__init__(self, 'qccr', thread_cnt=thread_cnt, queue_size=queue_size)
        self.parser = QccrParser(self)

    def dispatcher(self, q):
        for min, max in QccrDATA.p:
            self.add_main_job({'url_template':QccrDATA.url_template, 'min':min, 'max':max, 'page':1, 'mainjob':1})

    def run_job(self, job):
        if not job:
            return

        min = job.get('min')
        max = job.get('max')
        page = job.get('page')
        url = job.get('url_template') % (min, max, page)

        resp = self.request_url(url)
        if resp:
            items = self.parser.parse(resp.text, job)
            self.saveItems(items)


if __name__ == '__main__':
    s = QccrSpider(1)
    s.run()