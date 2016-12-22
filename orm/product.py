#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from orm.base import Model, StringField, IntegerField, FloatField, LongField
from store.impl_mgo.product_store import ProductStore

class Product(Model):

    itemId = StringField(primary_key=True)
    name = StringField()
    price = FloatField()
    brand = StringField()
    source = StringField()
    createTime = LongField()
    updateTime = LongField()
    url = StringField()

    db_config = {

        "mongo_storer": ProductStore(),

        # 用来切换数据库
        "switch": {

            "mongo": 1,
            "file": 0,
        }
    }

if __name__ == '__main__':
    p = Product()
    p._id = "1234"
    p.name = "xxxx"
    p.price = 32
    p.brand = "htw"
    p.source = "td"
    p.itemId = "hao"
    p.createTime = 123214
    p.updateTime = 123123123

    p.insert()

