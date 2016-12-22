#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from parsers.base import TypeParse
from lxml import html


class TqdkParser(TypeParse):
    def __init__(self, spider):
        TypeParse.__init__(self, spider)

    def parse(self, resp, job):
        if isinstance(resp, unicode):
            resp = resp.encode('utf-8')

        doc = html.fromstring(resp)

        print doc