#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

class TyreStoreFactory(object):

    @classmethod
    def getTyreStore(cls, db_type="mongo"):
        if db_type == "mongo":
            from store.impl_mgo.tyre_store import TyreStore
            return TyreStore()

        if db_type == "file":
            from store.impl_file.tyre_store import TyreFileStore
            return TyreFileStore()