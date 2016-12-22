#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from store.base_store import BaseStore
import pymongo
import os
import ConfigParser


class BaseMgoStore(BaseStore):
    def __init__(self, mongo_url=None):
        BaseStore.__init__(self)

        self.mongo_url = mongo_url
        if not self.mongo_url:
            self.mongo_url="mongodb://127.0.0.1/test"

        if not getattr(self, "db_name", ""):
            self.db_name = "test"
        if not getattr(self, "coll_name", ""):
            self.coll_name = "test"
        self.mongo_client = pymongo.MongoClient(self.mongo_url)[self.db_name][self.coll_name]

    @classmethod
    def load_mongo_conf(cls, section):
        mongo_conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../conf/mongo_conf.ini")
        config = ConfigParser.ConfigParser()
        config.readfp(open(mongo_conf_path, "rb"))

        mongo_url, db_name, coll_name = None, None, None

        MGO_URL = "mongo_url"
        MGO_DB = "mongo_db"
        MGO_COLL = "mongo_coll"

        if config.has_option(section, MGO_URL):
            mongo_url = config.get("battery", MGO_URL)
        else:
            mongo_url = config.get("common", MGO_URL)

        if config.has_option(section, MGO_DB):
            db_name = config.get(section, MGO_DB)
        else:
            db_name = config.get("common", MGO_DB)

        if config.has_option(section, MGO_COLL):
            coll_name = config.get(section, MGO_COLL)
        else:
            coll_name = config.get("common", MGO_COLL)

        return mongo_url, db_name, coll_name

    def test_mongo(self):
        self.mongo_client.update({"name": "jianghao"}, {"name":"jianghao", "age": 18}, upsert=True)
        print self.mongo_client.find_one({"name":"jianghao"})

    def insert(self, key, param):
        self.mongo_client.update(key, param, upsert=True)

    def find(self, key):
        return self.mongo_client.find(key)


if __name__ == '__main__':
    s = BaseMgoStore()
    s.test_mongo()
