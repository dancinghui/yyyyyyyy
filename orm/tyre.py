#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from orm.base import Model, StringField, FloatField, LongField
from store.impl_mgo.tyre_store import TyreStore
from store.impl_file.tyre_store import TyreFileStore


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
        "file_storer":TyreFileStore(),

        # 用来切换数据库
        "switch": {

            "mongo": 1,
            "file": 1,
        }
    }

if __name__ == '__main__':
    t = Tyre()
    t.name = "123"
    t.insert("file")