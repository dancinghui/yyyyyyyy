#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base_spider import BaseSpider
from parsers.qipeilong import QipeilongParser


class QipeilongDATA(object):

    SOURCE = "qipeilong"

    URL = "http://www.qipeilong.cn/Parties/Product/GetProductsForPc"

    POST_DATA_TEMPLATE = "Keyword=&Page=%d&brandId=&catalogId=301&extParam=&modelType=1&orderType=&pageSize=20&productId=&userId=6c005a998a9d4b02adc72b7e80df25f7"


class QipeilongSpider(BaseSpider):
    def __init__(self, thread_cnt=10, queue_size=200):
        BaseSpider.__init__(self, QipeilongDATA.SOURCE, queue_size=queue_size, thread_cnt=thread_cnt)
        self.parser = QipeilongParser(self)

    def dispatcher(self, q):
        job = {'page':1, 'mainjob':1}
        self.add_main_job(job)

    def run_job(self, job):
        if not job:
            return
        data = QipeilongDATA.POST_DATA_TEMPLATE % job.get('page')
        resp = self.request_url(QipeilongDATA.URL, data=data)
        if resp:
            items = self.parser.parse(resp.text, job)
            self.saveItems(items)


if __name__ == '__main__':
    s = QipeilongSpider(4)
    s.run()