#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base_spider import BaseSpider
from parsers.tqdk import TqdkParser


class TqdkDATA(object):
    SOURCE = 'tqdk'
    URL_TEMPLATE = 'http://www.tqmall.com/Tire.html?catSecId=197&p=%d'


class TqdkSpider(BaseSpider):
    def __init__(self, thread_cnt=10, queue_size=200):
        BaseSpider.__init__(self, TqdkDATA.SOURCE, thread_cnt=thread_cnt,  queue_size=queue_size)
        self.parser = TqdkParser(self)
        self.init_session()

    def init_session(self):
        self.session_request.add_cookie('tqmall.com', 'user_display_name', '13612729997')
        self.session_request.add_cookie('tqmall.com', 'user_id', '301dIDwMb87iFTVfpprf53uCPHysRW71rDS%2Bu4Nc1055CUM')
        self.session_request.add_cookie('tqmall.com', 'account_id', '44dikLCAqgx5KggQgjf5HjqpFyqlZvvWTSz4uXMtE2Brm0')
        self.session_request.add_cookie('tqmall.com', 'user_display_name', '13612729997')
        self.session_request.add_cookie('tqmall.com', 'user_id', '301dIDwMb87iFTVfpprf53uCPHysRW71rDS%2Bu4Nc1055CUM')
        self.session_request.add_cookie('tqmall.com', 'account_id', '44dikLCAqgx5KggQgjf5HjqpFyqlZvvWTSz4uXMtE2Brm0')

    def dispatcher(self, q):
        self.add_main_job({'page':1, 'mainjob':1})

    def run_job(self, job):
        if not job:
            return

        url = TqdkDATA.URL_TEMPLATE % job.get('page')
        resp = self.session_request.request_url(url)
        if resp:
            items = self.parser.parse(resp.text, job)
            self.saveItems(items)




if __name__ == '__main__':
    s = TqdkSpider(1)
    s.run()

