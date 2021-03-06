#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikem#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from store.base_mongo_store import BaseMgoStore


class ProductStore(BaseMgoStore):
    def __init__(self):
        self.mongo_url, self.db_name, self.coll_name = self.load_mongo_conf("product")
        BaseMgoStore.__init__(self, self.mongo_url)


if __name__ == '__main__':
    s = ProductStore()
    print s.mongo_url, s.db_name, s.coll_name
