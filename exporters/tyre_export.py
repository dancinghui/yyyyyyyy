#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from exporters.base import BasicExport
from orm.tyre import Tyre


class TyreExport(BasicExport):
    def __init__(self, query=None, thread_cnt=1):
        BasicExport.__init__(self, 'tyreExport', query=query, thread_cnt=thread_cnt)

    def dispatcher(self, q):
        if not self.query:
            self.query = {}

        for item in Tyre.get(self.query):
            if not self.file_path:
                self.file_path = item.export_file_path()
            self.add_main_job({"item":item})

    def run_job(self, job):
        if not job:
            return
        item = job.get("item")
        item.insert("file")


if __name__ == '__main__':
    s = TyreExport({})
    s.run()
