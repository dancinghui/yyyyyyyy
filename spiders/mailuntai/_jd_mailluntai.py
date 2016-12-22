#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base_spider import BaseSpider
from parsers.mailluntai import JdMailuntaiParser


class MailluntaiGlobleData(object):
    # url = "http://mall.jd.com/index-31590.html"
    url_template = 'http://search.jd.com/Search?keyword=麦轮胎&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&stock=1&s=%d&click=0&page=%d'

class MailuntaiSpider(BaseSpider):
    def __init__(self, thread_cnt=10, queue_size=200):
        BaseSpider.__init__(self, 'mailuntai', queue_size=queue_size, thread_cnt=thread_cnt)
        self.parser = JdMailuntaiParser(self)

    def dispatcher(self, q):
        self.add_main_job({'url':MailluntaiGlobleData.url_template, 'mainjob':1, 'page':1})

    def run_job(self, job):
        if not job:
            return

        s = job.get('s')
        page = job.get('page')
        resp = self.request_url(job.get('url') % (s, page))
        if resp:
            items = self.parser.parse(resp.text, job)
            self.saveItems(items)


if __name__ == '__main__':
    s = MailuntaiSpider(1)
    s.run()
