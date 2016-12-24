#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from store.base_file_store import BaseFileStore
from util.file_util import CsvFile


class TyreFileStore(BaseFileStore):
    def __init__(self):
        BaseFileStore.__init__(self, file_save_class=CsvFile)
        self.load_file_config("tyre")

        if self.file_save_class == CsvFile:
            self.is_set_header = False
            self.check_headers()

    def check_headers(self):
        with open(self.file_save_path, 'rb') as f:
            for line in f:
                if line.strip():
                    self.is_set_header=True
                    break

    def insert(self, key, params):
        if not self.is_set_header:
            from orm.tyre import Tyre
            self.headers = self.set_csv_headers(Tyre.__default_export_fields__)

        row = [params.get(key, "") for key in self.headers]
        self.client.append_row(row)
