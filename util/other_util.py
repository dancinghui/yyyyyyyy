#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

import json
import time

def utf8str(obj):
    if isinstance(obj, unicode):
        return obj.encode('utf-8')
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict) or isinstance(obj, list):
        return utf8str(json.dumps(obj, ensure_ascii=False, sort_keys=True))
    return utf8str(str(obj))


class TimeUtil(object):

    @classmethod
    def get_today_time_str(cls):
        now = time.localtime()
        return "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)



if __name__ == '__main__':
    print TimeUtil.get_today_time_str()

