#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'


import threading
import sys
import os
import ctypes
import StringIO
import re
import struct
import gzip
import time
import json
reload(sys)

class Runtime(object):
    namelock = threading.RLock()
    namemap = {}

    @staticmethod
    def get_thread_name(tid):
        with Runtime.namelock:
            return Runtime.namemap.get(tid, '')

    @staticmethod
    def set_thread_name(tid, name):
        with Runtime.namelock:
            Runtime.namemap[tid] = name

    @staticmethod
    def current_thread():
        return threading.current_thread().ident

    @staticmethod
    def set_current_thread_name(name):
        return Runtime.set_thread_name(Runtime.current_thread(), name)


Runtime.set_current_thread_name('main')


class Color(object):
    WIN_INITED = False
    @staticmethod
    def enable_windows():
        if os.name != 'nt':
            return
        if Color.WIN_INITED:
            return
        Color.WIN_INITED = True
        # build ansicon and load the dlls for ansi colors on windows cmd console
        try:
            if struct.calcsize("P") == 4:
                ctypes.windll.LoadLibrary("ansi32.dll")
            else:
                ctypes.windll.LoadLibrary("ansi64.dll")
        except:
            pass

    @staticmethod
    def parse_color(s, kv):
        sset, fore, back = 1000,2000,3000
        kvtable = {
            'bold' : [sset,1],
            'bright' : [sset,1],
            'dim': [sset, 2],
            'underlined': [sset, 4],
            'underline': [sset, 4],
            'blink': [sset, 5],
            'reverse': [sset, 7],
            'hidden': [sset, 8],

            "black":[fore,30],
            "red":[fore,31],
            "green":[fore,32],
            "yellow":[fore,33],
            "blue":[fore,34],
            "magenta":[fore,35],
            "cyan":[fore,36],
            "light gray":[fore,37],
            "gray":[fore,37],
            "dark gray":[fore,90],
            "light red":[fore,91],
            "light green":[fore,92],
            "light yellow":[fore,93],
            "light blue":[fore,94],
            "light magenta":[fore,95],
            "light cyan":[fore,96],
            "white":[fore,97],

            "_black":[back,40],
            "_red":[back,41],
            "_green":[back,42],
            "_yellow":[back,43],
            "_blue":[back,44],
            "_magenta":[back,45],
            "_cyan":[back,46],
            "light _gray":[back,47],
            "_gray":[back,47],
            "dark _gray":[back,100],
            "light _red":[back,101],
            "light _green":[back,102],
            "light _yellow":[back,103],
            "light _blue":[back,104],
            "light _magenta":[back,105],
            "light _cyan":[back,106],
            "_white":[back,107],
        }
        s = s.lower()
        if s in kvtable:
            a = kvtable[s]
            if a[0] == sset:
                kv[a[0]+a[1]] = a[1]
            else:
                kv[a[0]] = a[1]

    def __init__(self, colorstr, fd=sys.stdout, newline = ''):
        Color.enable_windows()
        if isinstance(colorstr, str) or isinstance(colorstr, unicode):
            s = re.sub(r'\s+', '   ', colorstr)
            s = re.sub(r'(dark|light)\s+', r'\1 ', s)
            colorstr = re.split(r'\s\s+', s)
        elif isinstance(colorstr, list):
            pass
        else:
            raise ValueError()
        codes = {}
        for i in colorstr:
            Color.parse_color(i, codes)
        vs = codes.values()
        vs.sort()
        rs = "\033["
        if len(vs) > 0:
            for i in vs:
                rs += "%d;" % i
            rs = rs[0:-1] + 'm'
            self.header = rs
        else:
            self.header = ''
        self.tail = "\033[0m"
        self.fd = fd
        self.newline = newline

    def __enter__(self):
        if self.header:
            self.fd.write(self.header)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.write(self.tail + self.newline)

    def qstr(self, s):
        return self.header + s + self.tail

    def _println(self, v):
        with self:
            idx = 0
            for i in v:
                if isinstance(i, unicode):
                    i = i.encode('utf-8')
                if idx > 0:
                    self.fd.write(' ')
                self.fd.write(str(i))
                idx += 1
        self.fd.write("\n")


class Log(object):
    outputlock = threading.RLock()

    @staticmethod
    def _compress_item(name, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        fo = StringIO.StringIO()
        f = gzip.GzipFile(fileobj=fo, mode='wb')
        f.write(value)
        f.close()
        r = fo.getvalue()
        fo.close()
        return struct.pack("I", len(name)) + name + struct.pack("I", len(r)) + r

    @staticmethod
    def warning(*v):
        with Log.outputlock:
            return Color('bold yellow _gray', sys.stderr)._println(v)

    @staticmethod
    def info(*v):
        with Log.outputlock:
            return Color('', sys.stdout)._println(v)

    @staticmethod
    def error(*v):
        ts = [time.strftime('%Y-%m-%d %H:%M:%S')]
        ts.extend(v)
        with Log.outputlock:
            Log._error_save_i(ts)
            return Color('bold red', sys.stderr)._println(v)

    @staticmethod
    def errorbin(msg, bin):
        obin = Log._compress_item(msg, bin)
        with Log.outputlock:
            try:
                with open('errorlog.bin', 'a+b') as fd:
                    fd.write(obin)
            except:
                pass

    @staticmethod
    def errinfo(*v):
        with Log.outputlock:
            return Color('', sys.stderr)._println(v)

    @staticmethod
    def _println_f(fd, v):
        idx = 0
        for i in v:
            if isinstance(i, unicode):
                i = i.encode('utf-8')
            if idx > 0:
                fd.write(' ')
            fd.write(str(i))
            idx += 1
        fd.write("\n")

    @staticmethod
    def _error_save_i(v):
        try:
            with open('errorlog.log', 'a+b') as fd:
                Log._println_f(fd, v)
        except:
            pass
