#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from parsers.base import JdTyreParse
from lxml import html
from orm.tyre import Tyre
import time


class JdMailuntaiParser(JdTyreParse):
    def __init__(self, spider):
        JdTyreParse.__init__(self, spider)




