#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from store.base_file_store import BaseFileStore
from util.file_util import CsvFile


class BatteryFileStore(BaseFileStore):
    def __init__(self):
        BaseFileStore.__init__(self, file_save_class=CsvFile)
        self.load_file_config("battery")

        if self.file_save_class == CsvFile:
            self.is_set_header = False
            self.check_headers()

    def check_headers(self):
        with open(self.file_save_path, 'rb') as f:
            for line in f:
                if line.strip():
                    self.is_set_header=True

    def set_csv_headers(self, params):
        keys = sorted(params.keys())
        self.client.set_header(keys)
        self.is_set_header = True

    def insert(self, key, params):
        if not self.is_set_header:
            self.set_csv_headers(params)

        row = []
        for key in sorted(params.keys()):
            row.append(params[key])

        self.client.append_row(row)




