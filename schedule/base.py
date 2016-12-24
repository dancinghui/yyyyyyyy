#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

import os
import re
import multiprocessing
from spiders.base.runtime import Log
import sys
import json

def runner_run(runner):
    globals()['%s_instance' % runner].run()


class ScanUtil(object):

    @staticmethod
    def convert(path):

        if not path.startswith('/'):
            raise Exception("just used convert abs path")

        ret = []
        for partion in path.split('/'):

            if partion == '..':
                ret.pop()
                continue
            else:
                ret.append(partion)

        return '/'.join(ret)



    @staticmethod
    def _import_pkg(name, path, f):
        path = ScanUtil.convert(path)
        partions = path.split('/')

        _index = partions.index('crawler')
        pkg_name = '.'.join(partions[_index+1:] + [f.split('.py')[0]])

        _import_str = 'from %s import %s' % (pkg_name, name)
        Log.info("do import pkg : %s" % _import_str)
        exec _import_str
        globals()[name] = locals()[name]

    @staticmethod
    def find_pattern(path, f, pattern):
        if not f.endswith('.py'):
            return

        if f in ['__init__.py']:
            return

        file_name = os.path.join(path, f)
        with open(file_name, 'rb') as f1:
            content = f1.read()

        find = re.search(pattern, content)
        if find:
            clz_name = find.group(1)
            ScanUtil._import_pkg(clz_name, path, f)
            return clz_name


class BaseSchedule(object):

    def __init__(self, name, thread_cnt=2):
        self.thread_cnt = thread_cnt
        self._name = name
        self.all_runners = []

    def get_runners(self):
        raise NotImplementedError("virtual function called")

    def get_instance(self, name, **kwargs):
        return globals()[name](**kwargs)

    def run(self):
        runners = self.get_runners()
        if len(runners) == 0:
            Log.warning("[ - ] there is no %s run" % self._name)
            return
        Log.info("================== %s list start=========================" % self._name)
        for name, instance in runners.items():
            globals()["%s_instance" % name] = instance
            Log.info(name)

        Log.info("================== %s list end ==========================" % self._name)

        pool = multiprocessing.Pool(processes=len(runners))
        for name, instance in runners.items():
            pool.apply_async(runner_run, args=(name, ))
            Log.info("[ + ] %s started:  " % name)

        pool.close()
        pool.join()

    def parse_param(self, flag):
        ret = dict()

        print sys.argv
        if flag not in sys.argv[1:]:
            Log.info("[ + ] %s can schedule: \n\n" % self._name, "\n".join(list(self.all_runners)))
            return ret

        index_ = sys.argv.index(flag)
        runners = sys.argv[index_ + 1].split(',')

        for runner in runners:
            e = runner.split(':', 2)
            t_cnt = self.thread_cnt
            name = e[0]
            if name not in self.all_runners:
                continue
            clz_param = {}


            i = -1
            for part in e:
                i += 1
                if i == 0:
                    continue
                if i == 1:
                    t_cnt = int(part)
                if i == 2:
                    clz_param = json.loads(part)

            clz_param.update({'thread_cnt':t_cnt})

            exporter_instance = self.get_instance(name, **clz_param)
            ret[name] = exporter_instance

        return ret


if __name__ == '__main__':
    print ScanUtil.convert('/a/b/c/../d')