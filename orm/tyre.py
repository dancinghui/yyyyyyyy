#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from orm.base import Model, StringField, FloatField, LongField
from store.impl_mgo.tyre_store import TyreStore


class Tyre(Model):

    itemId = StringField(primary_key=True)
    name = StringField()
    price = FloatField()
    width = StringField()
    rat = StringField()
    rim = StringField()

    source = StringField()
    createTime = LongField()
    updateTime = LongField()
    pattern = StringField()
    speed = StringField()
    specs = StringField()
    url = StringField()

    db_config = {

        "mongo_storer": TyreStore(),

        # 用来切换数据库
        "switch": {

            "mongo": 1,
            "file": 0,
        }
    }

if __name__ == '__main__':
    t = Tyre()
    r = t.get({})
    for s in r:
        print s
    # print r