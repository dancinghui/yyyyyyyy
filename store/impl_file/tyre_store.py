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

    def insert(self, key, params):
        if not self.is_set_header:
            from orm.tyre import Tyre
            self.header_keys = Tyre.__default_export_fields__
            self.headers = [Tyre.__mapping_keys_desc__[k] for k in self.header_keys]

            self.set_csv_headers(self.headers)

        row = [params.get(key, "") for key in self.header_keys]
        self.client.append_row(row)
