#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'


from orm.tyre import Tyre
from lxml import html
import time
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Parse(object):
    def __init__(self, spider):
        self.spider = spider
        self.source = self.spider.task_name

    def add_job(self, job):
        self.spider.add_sub_job(job)

    def parse(self, resp, job):
        pass

    @staticmethod
    def remove_tag(s, fmt=False):
        s = s.strip()
        if fmt:
            r = re.sub(r'<br>|<p>|<BR>', '\n', s)
            r = re.sub(r'(<[^>]*>)', '', r)
            r = re.sub(r'&nbsp;', ' ', r)
            r = re.sub(r'[\t\r ]+', ' ', r)
            r = re.sub(r'\s+\n+\s+', '\n', r)

            r = re.sub(r'^\s+', '', r)
            r = re.sub(r'\s+$', '', r)

            r = re.sub(r'\xc2\xa0$', '', r)
            r = re.sub(r'^\xe3\x80', '', r)

        else:
            r = re.sub(r'(<[^>]*>)', '', s)
            r = re.sub(r'&nbsp;', ' ', r)
            r = re.sub(r'\xc2\xa0$', '', r)
            r = re.sub(r'^\xe3\x80', '', r)
        return r

    @classmethod
    def format_price(cls, price):

        if isinstance(price, unicode):
             price = price.encode('utf-8')

        find = re.search(r'(\d+)元', price) #定价：296元
        if find:
            return float(find.group(1))

        price = re.sub('[¥,]', '', price)

        return float(price)


class TypeParse(Parse):
    def __init__(self, spider):
        Parse.__init__(self, spider)

    @classmethod
    def get_spec_pattern(cls, job, title):
        find = re.search('(\d+/\d+[A-Z]{1,2}[A-Z\d]+)', title)
        if find:
            return find.group(1)

        print "unknow title pattern: %s" % title
        return None

    @classmethod
    def get_pattern_speed(cls, name, specs, patternFirst=True):

        name_partions = name.split()
        i = -1
        specs_index = -1
        for part in name_partions:
            i += 1
            if specs in part:
                specs_index = i
                break

        if patternFirst:
            try:
                pattern = name_partions[specs_index - 1]
                speed = name_partions[specs_index + 1]
                return pattern, speed
            except IndexError:
                pass

        return None, None

    @classmethod
    def getWidthRatRim(cls, specs):
        one_part = specs.split('/')

        if 'ZR' in specs:
            second_part = one_part[1].split('ZR')
        else:
            second_part = one_part[1].split('R')

        return one_part[0], second_part[0], second_part[1]


    def genItem(self, preItem):
        item = Tyre()
        item.itemId = preItem["itemId"]
        item.url = preItem["itemUrl"]
        item.name = preItem["name"]
        item.source = preItem["source"]
        item.createTime = preItem["createTimeStamp"]
        item.updateTime = preItem["updateTimeStamp"]
        item.price = preItem["price"]
        item.width = preItem["width"]
        item.rat = preItem["rat"]
        item.rim = preItem["rim"]
        item.pattern = preItem["pattern"]
        item.specs = preItem["specs"]
        item.speed = preItem["speed"]

        return item

class JdTyreParse(TypeParse):
    def __init__(self, spider):
        TypeParse.__init__(self, spider)



    def parse(self, resp, job):

        ret = []
        if isinstance(resp, unicode):
            resp = resp.encode('utf-8')

        doc = html.fromstring(resp)

        if "mainjob" in job:
            self.fetch_sub_jobs(job, doc)

        li_els = doc.xpath("//div[@id='J_goodsList']//li[@class='gl-item']")
        # prices = self.extract_price(doc)

        for li_el in li_els:
            name_el = li_el.xpath('.//div[starts-with(@class, "p-name")]//em')
            if not name_el:
                print "found no name"
                continue
            name = name_el[0].xpath('string(.)')
            name = self.remove_tag(name, 1)
            price_el = li_el.xpath(".//div[@class='p-price']/strong/i")
            if not price_el:
                print "found no price"
                continue

            price = float(price_el[0].text.strip())

            specs = self.get_spec_pattern(job, name)

            if not specs:
                print "found no specs"
                continue

            width, rat, rim = self.getWidthRatRim(specs)

            try:
                pattern, speed = self.get_pattern_speed(name, specs)
            except:
                print "get pattern speed fail, title: %s" % name
                continue

            now = int(time.time() * 1000)

            href = li_el.xpath(".//a/@href")[0]

            if href.startswith('//'):
                href = "http:"+href

            itemId = href.split('/')[-1].split('.')[0]

            m = {
                'name':name,
                'price':price,
                'width':width,
                'rat':rat,
                'rim':rim,
                'source':self.source,
                'itemId':itemId,
                'createTimeStamp':now,
                'updateTimeStamp':now,
                'pattern':pattern,
                'speed':speed,
                'specs':specs,
                'itemUrl':href
            }

            item = self.genItem(m)
            ret.append(item)

        return ret

    def fetch_sub_jobs(self, job, doc):
        el = doc.xpath("//div[@id='J_topPage']/span/i")
        if not el:
            return
        totalPage = int(el[0].text.strip())
        for i in range(2, totalPage+1):
            if i % 2 == 0:
                continue
            new_ = {'url':job.get('url'), 'page':i, 's':30*i+1-30}

            self.add_job(new_)

            new_ = {'url': job.get('url'), 'page': i, 's': 30 * i + 1 - 30*2}

            self.add_job(new_)

if __name__ == '__main__':
    print Parse.format_price('¥1,408.00')