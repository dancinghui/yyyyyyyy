#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base_spider import BaseSpider
from parsers.qccr import QchParser


class QchDATA(object):
    SOURCE_NAME = 'qch'
    URL_TEMPLATE = 'http://pch.qccr.com/goods/list/tire.jhtml?data=' \
                   '{"brandId":"0","carCategoryId":0,"categoryId":10,"isFB":0,"speedLevel":0,"tireModelId":0,"tireSpec":"0","orderField":0,"orderType":0,"pageNum":%d,"pageSize":25}'


class QchSpider(BaseSpider):
    def __init__(self, thread_cnt=10, queue_size=200):
        BaseSpider.__init__(self, spider_name=QchDATA.SOURCE_NAME, thread_cnt=thread_cnt, queue_size=queue_size)
        self.parser = QchParser(self)

    def dispatcher(self, q):
        self.add_main_job({'url_template': QchDATA.URL_TEMPLATE, 'page':1, 'mainjob':1})

    def run_job(self, job):
        if not job:
            return

        url = job.get('url_template') % job.get('page')
        resp = self.request_url(url)
        if resp:
            items = self.parser.parse(resp.text, job)
            self.saveItems(items)


if __name__ == '__main__':
    s = QchSpider(1)
    s.run()
