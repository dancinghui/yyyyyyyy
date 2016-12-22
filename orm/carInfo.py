#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from orm.base import Model, StringField, IntegerField
from store.impl_mgo.carInfo_store import CarInfoStore


class CarInfo(Model):

    carModelId = IntegerField(primary_key=True)
    seriesName = StringField()
    modelName = StringField()
    brandName = StringField()
    battery = StringField()

    db_config = {

        "mongo_storer": CarInfoStore(),

        # 用来切换数据库
        "switch": {

            "mongo": 1,
            "file": 0,
        }
    }


if __name__ == '__main__':

    def save(i):
        s = CarInfo()
        s._id = i
        s.carModelId = 444
        s.seriesName = "345"
        s.modelName = "xxx"
        s.brandName = "htw"
        s.battery = "battery"
        s.insert()


    import threading
    threads = []
    for i in range(10):
        t = threading.Thread(target=save, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print "OK"


