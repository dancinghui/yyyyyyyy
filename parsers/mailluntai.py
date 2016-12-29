#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from parsers.base import JdTyreParse, TypeParse
from lxml import html
import copy
import re
import time


class JdMailuntaiParser(JdTyreParse):
    def __init__(self, spider):
        JdTyreParse.__init__(self, spider)


class MailuntaiParser(TypeParse):
    def __init__(self, spider):
        TypeParse.__init__(self, spider)

    def parse(self, resp, job):

        ret = []
        if isinstance(resp, unicode):
            resp = resp.encode("utf-8")

        doc = html.fromstring(resp)

        self.check_next_page(job, doc)

        els = doc.xpath("//div[@class='nodata']")
        if els:
            return ret

        a_els = doc.xpath("//a[starts-with(@href, '/mproduct/info/')]")
        for a_el in a_els:
            print a_el

            sub_els = a_el.xpath(".//p[@class='f12']")
            if len(sub_els) < 2:
                continue

            name = sub_els[0].text.strip()
            price = self.format_price(sub_els[1].text)

            print name, price

            specs = self.get_spec_pattern(job, name)
            width, rat, rim = self.getWidthRatRim(specs)
            pattern, speed = self.get_pattern_speed(name, specs)

            itemUrl = "http://bd.mailuntai.cn" + a_el.attrib["href"]
            itemId = a_el.attrib['href'].split('/')[-1]
            now = int(time.time() * 1000)

            pre_item = {

                "name": name,
                "price": price,
                "width": width,
                "rat": rat,
                "rim": rim,
                "source": self.source,
                "itemId": itemId,
                "itemUrl": itemUrl,
                "createTimeStamp": now,
                "updateTimeStamp": now,
                "pattern": pattern,
                "speed": speed,
                "specs": specs
            }

            ret.append(self.genItem(pre_item))

        return ret



    def check_next_page(self, job, doc):
        els = doc.xpath("//a[starts-with(@href, '/mproducts/?') and contains(@href, 'page=') and @class='fr']")
        for el in els:
            find = re.search(r'page=(\d+)', el.attrib["href"])
            if find:
                new_ = copy.deepcopy(job)
                new_['page'] = find.group(1)
                self.add_job(new_)




