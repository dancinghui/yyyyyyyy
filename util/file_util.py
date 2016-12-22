#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'
import codecs
import csv
import threading


class CsvFile(object):
    def __init__(self, fn, mod='wb'):
        self.fn = fn
        self.csv_file = codecs.open(fn, mod, 'utf-8')
        self.writer = csv.writer(self.csv_file)
        self._lock = threading.RLock()

        self.is_set_header = False

    def __del__(self):
       with self._lock:
           self.csv_file.close()

    def set_header(self, header):
        if not isinstance(header, list):
            raise Exception('need list')

        with self._lock:
            if self.is_set_header:
                return
            self.writer.writerow(header)
            self.is_set_header = True

    def append_row(self, row):

        with self._lock:
            self.writer.writerow(row)

    def append_rows(self, rows):

        with self._lock:
            self.writer.writerow(rows)


if __name__ == '__main__':
    c = CsvFile("csv_test", 'a+')
    c.append_row(["jianghao", 123, 123])