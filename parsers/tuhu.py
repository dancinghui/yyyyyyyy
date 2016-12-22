#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from parsers.base import JdTyreParse, TypeParse
from lxml import html
import re
import copy
import math
import time


class TuhuParse(TypeParse):

    def __init__(self, q):
        TypeParse.__init__(self, q)

    def parse(self, resp, job):

        # check if is first page , continue dispatch the next page
        if isinstance(resp, unicode):
            resp = resp.encode('utf-8')

        doc = html.fromstring(resp)
        items = self.get_list(doc, job)

        return items

    def get_list(self, doc, job):

        ret = []

        els = doc.xpath("//b[@class='currentPage']/text()")

        # if is first page, dispatch the next pages
        if els and els[0].strip() == '1':
            totalItemEls = doc.xpath("//div[@class='listResult']/span[@class='totalItem']/text()")
            if totalItemEls:
                find = re.search('(\d+)', totalItemEls[0])
                if find:
                    totalItem = int(find.group(1))
                    totalPage = int(math.ceil(totalItem / 20.0))
                    if totalItem > 1:
                        for i in range(2,totalPage+1):
                            new_ = copy.deepcopy(job)
                            new_.update({'page':i})
                            self.add_job(new_)

        trs = doc.xpath("//table[@class='List']/tbody/tr")
        if not trs:
            return ret

        for tr in trs:
            el_title = tr.xpath('.//a[starts-with(@class, "DisplayName")]')[0]
            price = tr.xpath('.//div[@class="price"]/strong/text()')[0]
            price = self.format_price(price)

            title = self.remove_tag(el_title.text, 1)
            if not title:
                el_span = tr.xpath('.//a[starts-with(@class, "DisplayName")]/span[@class="prompt"]')[0]
                title = self.remove_tag(el_span.tail, 1)

            itemUrl = el_title.attrib["href"]

            specs = self.get_spec_pattern(job, title)
            if not specs:
                continue

            itemId = itemUrl[itemUrl.index("Products/")+9:]

            partions = title.split()
            spesc_index = partions.index(specs)
            pattern = partions[spesc_index-1]
            speed = partions[spesc_index+1]

            now = int(time.time() * 1000)

            pre_item = {

                "name": title,
                "price": price,
                "width": job.get("width"),
                "rat":job.get("rat"),
                "rim":job.get("rim"),
                "source": "tuhu",
                "itemId": itemId,
                "itemUrl": itemUrl,
                "createTimeStamp":now,
                "updateTimeStamp":now,
                "pattern":pattern,
                "speed" : speed,
                "specs":specs
            }

            ret.append(self.genItem(pre_item))

        return ret


class JdTuhuParse(JdTyreParse):
    def __init__(self, spider):
        JdTyreParse.__init__(self, spider)
























