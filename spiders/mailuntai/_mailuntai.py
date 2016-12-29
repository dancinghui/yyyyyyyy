#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base_spider import BaseSpider
from parsers.mailluntai import MailuntaiParser

class MailuntaiDATA(object):
    widths = ["155", "165", "165R13LT", "175", "185", "195", "205", "215", "225", "234", "235", "245",
             "255", "265", "275", "285", "295", "315"]

    rats = ['35', '40', '45', '50', '55', '60', '65','70','75','80','85']

    rims = {"11", "12", "12C", "13", "13C", "13LT", "14", "14C",
            "15", "15C", "16", "16.5", "16C", "17", "18", "19", "20", "21",
            "22", "23", "24", "26", "28", "45", "540", "V"}


    URL_TEMPLATE = "http://bd.mailuntai.cn/mproducts/?type=1&width=%s&rat=%s&rim=%s&speed=&page=%s"


class MailuntaiSpider(BaseSpider):
    def __init__(self, thread_cnt=10, queue_size=200):
        BaseSpider.__init__(self, "mailuntai", thread_cnt=thread_cnt, queue_size=queue_size)
        self.parser = MailuntaiParser(self)


    def dispatcher(self, q):
        for width in MailuntaiDATA.widths:
            for rat in MailuntaiDATA.rats:
                for rim in MailuntaiDATA.rims:
                    self.add_main_job({"width":width, "rat":rat, "rim":rim, 'page':1})
                    # self.add_main_job({"width": "185", "rat": "60", "rim": "15", "page":"1"})


    def run_job(self, job):
        if not job:
            return

        url = MailuntaiDATA.URL_TEMPLATE % (job['width'], job['rat'], job['rim'], job['page'])
        resp = self.request_url(url)
        if resp:
            items = self.parser.parse(resp.text, job)
            self.saveItems(items)


if __name__ == '__main__':
    s = MailuntaiSpider(1)
    s.run()
