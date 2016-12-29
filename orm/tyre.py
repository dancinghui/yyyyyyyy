#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from orm.base import Model, StringField, FloatField, LongField
from store.factory import TyreStoreFactory


class Tyre(Model):

    itemId = StringField(primary_key=True)
    name = StringField(desc="名称")
    price = FloatField(desc="价格")
    width = StringField(desc="胎面宽")
    rat = StringField(desc="扁平比")
    rim = StringField(desc="直径")

    source = StringField(desc="来源")
    createTime = LongField(desc="创建时间")
    updateTime = LongField(desc="更新时间")
    pattern = StringField(desc="花纹")
    speed = StringField(desc="级别")
    specs = StringField(desc="规格")
    url = StringField(desc="来源网址")

    db_config = {

        "mongo_storer": TyreStoreFactory.getTyreStore("mongo"),
        "file_storer":TyreStoreFactory.getTyreStore("file"),

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