#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from store.base_mongo_store import BaseMgoStore


class BatteryStore(BaseMgoStore):
    def __init__(self):
        self.mongo_url, self.db_name, self.coll_name = self.load_mongo_conf("battery")
        BaseMgoStore.__init__(self, self.mongo_url)


if __name__ == '__main__':
    s = BatteryStore()
    print s.mongo_url, s.db_name, s.coll_name