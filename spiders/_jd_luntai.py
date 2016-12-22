#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base_spider import BaseSpider
from parsers.jdluntai import JdLuntaiParser


class JdLuntaiGlobleData(object):
    PAGE_TEMPLATE = 'https://list.jd.com/list.html?cat=6728,6742,9248&page=%d&trans=1&JL=6_0_0&ms=6#J_main'

class JdLuntaiSpider(BaseSpider):

    def __init__(self, queue_size=200, thread_cnt=10):
        BaseSpider.__init__(self, 'jd_luntai', queue_size=queue_size, thread_cnt=thread_cnt)
        self.parser = JdLuntaiParser(self)


    def dispatcher(self, q):
        self.add_main_job({'url_template': JdLuntaiGlobleData.PAGE_TEMPLATE, 'page':1})


    def run_job(self, job):
        if not job:
            return

        url = job.get('url_template') % job.get('page')
        resp = self.request_url(url)
        if resp:
            self.parser.parse(resp.text, job)


if __name__ == '__main__':
    s = JdLuntaiSpider(1)
    s.run()