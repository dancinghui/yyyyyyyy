#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from parsers.base import Parse
from orm.product import Product
from lxml import html
import copy
import time


class HaolishiParser(Parse):
    def __init__(self, q):
        Parse.__init__(self, q)

    def parse(self, resp, job):

        ret = []
        if isinstance(resp, unicode):
            resp = resp.encode('utf-8')

        doc = html.fromstring(resp)

        if 'page' not in job:
            totalPage_el = doc.xpath('//div[@class="pagin pagin-m"]/span')[0]
            page_info = totalPage_el.xpath('string(.)').strip()
            current_page, total_page = page_info.split('/')
            if current_page == '1':
                for i in range(2, int(total_page) + 1):
                    new_ = copy.deepcopy(job)
                    new_.update({'page':i})
                    self.add_job(new_)

        brands = self.extract_brands(doc)
        li_els = doc.xpath('//li[@class="item"]')

        for li in li_els:
            goods_info_el = li.xpath('.//div[@class="goods-info"]')[0]
            goods_name_el = goods_info_el.xpath('.//div[@class="goods-name"]')[0]
            goods_price_el = goods_info_el.xpath('.//div[@class="goods-price"]')[0]

            goods_name = self.remove_tag(goods_name_el.xpath('string(.)'), 1)
            href = goods_name_el.xpath('./a/@href')[0]

            itemId = href.split('=')[1]

            goods_price = self.remove_tag(goods_price_el.xpath('string(.)'), 1)

            brand = self.get_brand(goods_name, brands)

            now = int(time.time() * 1000)
            item = self.genItem(goods_name, float(goods_price), brand, 'haolishi', now, now, itemId)
            ret.append(item)

        return ret

    def genItem(self, name, price, brand, source, createTime, updateTime, itemId):

        item = Product()
        item.itemId = itemId
        item.name = name
        item.price = price
        item.brand = brand
        item.source = source
        item.createTime = createTime
        item.updateTime = updateTime

        return item


    def get_brand(self, name, brands):
        for brand in brands:
            if brand in name:
                return brand

        return ''


    def extract_brands(self, doc):
        ret = []
        li_els = doc.xpath("//div[@id='brand_abox_father']//ul[@id='brand_abox']//li")
        for el in li_els:
            ret.append(el.xpath('@title')[0])

        return ret