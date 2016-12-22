#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'
from orm.base import Model, StringField, IntegerField
from store.impl_mgo.battery_store import BatteryStore
from store.impl_file.battery_store import BatteryFileStore


class Battery(Model):

    batteryId = IntegerField(primary_key=True)

    name = StringField()
    image = StringField()
    carModelId = IntegerField()

    db_config = {

        "mongo_storer": BatteryStore(),
        "file_storer": BatteryFileStore(),

        # 用来切换数据库
        "switch": {

            "mongo": 0,
            "file" : 1,
        }
    }




if __name__ == '__main__':
    b = Battery()
    b._id = "12345"
    b.name = "battery"
    b.image = "/sata"
    b.batteryId = 123
    b.carModelId = 323

    b.insert()
