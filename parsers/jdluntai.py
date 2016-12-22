#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from parsers.base import TypeParse
from lxml import html
import re
import copy

class JdLuntaiParser(TypeParse):
    def __init__(self, spider):
        TypeParse.__init__(self, spider)

    def parse(self, resp, job):


        ret = []
        if isinstance(resp, unicode):
            resp = resp.encode('utf-8')
        doc = html.fromstring(resp)

        if job.get('page') == 1:
            totalPage = doc.xpath('//div[@class="f-pager"]/span/i/text()')[0].strip()
            totalPage = int(totalPage)
            for i in range(2, totalPage+1):
                new_ = copy.deepcopy(job)
                new_.update({'page':i})
                self.add_job(new_)


        prices = self.extract_price(doc)

        li_els = doc.xpath("//li[@class='gl-item']")

        for li_el in li_els:
            itemId = li_el.xpath('.//div/@data-sku')[0]
            price = self.get_price(itemId, prices)

            p_name_el = li_el.xpath('.//div[@class="p-name"]')[0]
            href = p_name_el.xpath('.//a/@href')[0]
            name = p_name_el.xpath('.//a/em/text()')[0]

            spec = self.get_spec_pattern(job, name)



    def get_price(self, priceId, prices):
        id_ = "J_%s" % priceId
        return prices[id_]

    def extract_price(self, doc):
        ret = {}

        ids_ = doc.xpath('//div/@data-sku')
        urls = []
        if len(ids_) <= 30:
            urls.append(self.genPriceUrl(ids_[:30]))
        else:
            urls.append(self.genPriceUrl(ids_[:30]))
            urls.append(self.genPriceUrl(ids_[30:]))

        for url in urls:
            con = self.spider.request_url(url)
            l = eval(con.text[14:-3])
            print l
            for item in l:
                ret[item['id']] = item['p']

        return ret

    def genPriceUrl(self, ids_):
        url = 'https://p.3.cn/prices/mgets?callback=jQuery2297271&type=1&area=1_72_4137_0&skuIds='
        for id_ in ids_:
            url += 'J_%s,' % id_

        return url[0:-1]
