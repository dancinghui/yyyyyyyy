#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from parsers.base import TypeParse
import json
import time

class QipeilongParser(TypeParse):
    def __init__(self, spider):
        TypeParse.__init__(self, spider)


    def parse(self, resp, job):
        ret = []

        if isinstance(resp, unicode):
            resp = resp.encode('utf-8')

        resp_json = json.loads(resp)

        if "mainjob" in job:
            self.fetch_sub_jobs(resp_json)

        items = resp_json['Data']['Items']

        for item in items:
            itemId = item['UID']
            itemUrl = "http://www.qipeilong.cn/Parties/html/productdetail.html?i=%s" % itemId
            name = item["ProductName"]
            specs = self.get_spec_pattern(job, name)
            if not specs:
                continue
            width, rat, rim = self.getWidthRatRim(specs)
            price = item["MinListPrice"]
            now = int(time.time() * 1000)

            pattern, speed = self.get_pattern_speed(name, specs)
            if not pattern:
                continue

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


    def fetch_sub_jobs(self, resp_json):
        totalPage = resp_json['Data']['MaxPage']
        for i in range(2, totalPage+1):
            self.add_job({'page':i})