#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from parsers.base import TypeParse
from lxml import html
import time
import copy
import json

class QccrParser(TypeParse):
    def __init__(self, spider):
        TypeParse.__init__(self, spider)

    def parse(self, resp, job):

        ret = []
        if isinstance(resp, unicode):
            resp = resp.encode('utf-8')

        doc = html.fromstring(resp)

        if "mainjob" in job:
            self.fetch_sub_jobs(job, doc)

        li_els = doc.xpath('//div[@id="newResult"]//div[@class="thislist"]//li')

        for li_el in li_els:
            itemId = li_el.attrib['gid']
            itemUrl = li_el.xpath('.//a/@href')[0]
            name = li_el.xpath('.//a/@title')[0]
            price_el = li_el.xpath('.//p/span')
            if not price_el:
                print "not found price"
                continue

            price = price_el[0].xpath('string(.)')
            price = self.format_price(price)

            specs = self.get_spec_pattern(job, name)
            if not specs:
                continue
            width, rat, rim = self.getWidthRatRim(specs)

            pattern, speed = self.get_pattern_speed(name, specs)

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

            item = self.genItem(pre_item)
            ret.append(item)

        return ret

    def fetch_sub_jobs(self, jobs, doc):
        els = doc.xpath('//span[@class="allPage"]')
        if not els:
            return

        totalPage = int(els[0].text.strip())

        for i in range(2, totalPage+1):
            new_ = copy.deepcopy(jobs)
            del(new_['mainjob'])
            new_['page'] = i
            self.add_job(new_)


class QchParser(TypeParse):
    def __init__(self, spider):
        TypeParse.__init__(self, spider)

    def parse(self, resp, job):

        ret = []

        if isinstance(resp, unicode):
            resp = resp.encode('utf-8')

        json_resp = json.loads(resp)

        if "mainjob" in job:
            self.fetch_sub_jobs(job, json_resp)

        for item in json_resp['info']['itemVos']:
            itemId = item['itemId']
            itemUrl = "http://pch.qccr.com/goods/detail/%s.jhtml" % itemId
            price = item['webPrice']
            name = item['itemName']

            specs = self.get_spec_pattern(job, name)
            if not specs:
                print "found no specs"
                continue

            width, rat, rim = self.getWidthRatRim(specs)
            pattern, speed = self.get_pattern_speed(name, specs)

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


    def fetch_sub_jobs(self, job, json_resp):

        total = json_resp['info']['total']
        totalPage = (total + 25 - 1) / 25
        for i in range(2, totalPage+1):
            new_ = copy.deepcopy(job)
            del(new_["mainjob"])
            new_['page'] = i

            self.add_job(new_)

