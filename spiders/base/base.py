#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

import Queue
import time
import datetime
import threading
import traceback
import sys
import socket
import os
import json
import random
from ConfigParser import ConfigParser
from util.other_util import utf8str, TimeUtil
from spiders.base.runtime import Log
from spiders.base.exceptions import SpiderErrors, AccountErrors, LoginErrors
from util.mail import EmailHelper
from exepts.emailException import EmailInitException
reload(sys)
sys.setdefaultencoding('utf-8')


class BaseTask(object):


    def __init__(self, task_name, queue_size=200, thread_cnt=10):

        self.task_name = task_name
        self._queue = Queue.Queue(queue_size)
        self.job_queue2 = Queue.LifoQueue()
        self.job_queue3 = Queue.Queue()  # for failed jobs.
        self._thread_cnt = thread_cnt
        self._start_time = time.time()
        self._start_datetime = None
        self._running_count = 0
        self._work_count = 0
        self._threads = []
        self._reporter = None
        self._dispatcher = None
        self.cur_jobid = 0
        self._mjob_count = 0
        self._mjob_all = "?"
        self._log_port = 9527

        self._tls = threading.local()
        self._r_lock = threading.RLock()

        self.Default_EMAIL_RECEIVER = ["jianghao@91htw.com"]

    def add_main_job(self, job):
        while True:
            try:
                self._queue.put(job)
                return True
            except Queue.Full:
                if self._end_mark:
                    print "NO WORKER! failed to add job:", job
                    raise RuntimeError("no worker!")

    def add_sub_job(self, job):
        self.job_queue2.put(job)

    def add_fail_job(self, job):
        job['fail_time'] = job.get('fail_time', 0) + 1
        if job['fail_time'] < 3:
            self.job_queue3.put(job)
        else:
            self.save_fail_job(job)

    def dispatcher(self, q):
        raise NotImplementedError("virtual function called")

    def do_dispatcher(self, q):
        self.dispatcher(q)
        self.wait_q()
        self.add_main_job(None)

    def _job_runner(self, tid):
        with self._r_lock:
            self._work_count += 1
        setattr(self._tls, 'tid', tid)

        end_this_thread = False
        while not end_this_thread:
            job, is_main_job = self._get_job()
            if job is None:
                self._queue.put(None)
                self._dec_worker()
                return
            self.cur_jobid = job
            try:
                with self._r_lock:
                    self._running_count += 1
                self.run_job(job)
            except (AccountErrors.NoAccountError, SpiderErrors.FatalError) as e:
                Log.error(e)
                traceback.print_exc()
                end_this_thread = True
                self.add_fail_job(job)
            except (LoginErrors.RetryError, SpiderErrors.RetryError) as e:
                Log.error(e)
                traceback.print_exc()
                self.add_fail_job(job)
            except Exception as e:
                Log.warning(e)
                traceback.print_exc()
                self.add_fail_job(job)

            finally:
                with self._r_lock:
                    self._running_count -= 1

        self._dec_worker()

    def save_fail_job(self, job):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        cur_timestr = TimeUtil.get_today_time_str()
        save_path = os.path.join(cur_dir, '../../data/%s_fail_jobs_%s.txt' % (self.task_name, cur_timestr))
        with open(save_path, 'a+') as f:
            Log.info("saving fail job: %r" % job)
            f.write(json.dumps(job, ensure_ascii=False))
            f.write(os.linesep)

    def run_job(self, job):
        raise NotImplementedError("virtual function called")

    def _get_job(self):

        try:
            jobid = self.job_queue2.get_nowait()
            self.job_queue2.task_done()
            return jobid, False
        except Queue.Empty:
            pass

        if random.randint(1, 20) == 19:  # 以5%的概率拿一个已经失败的任务
            try:
                jobid = self.job_queue3.get_nowait()
                self.job_queue3.task_done()
                return jobid, False
            except Queue.Empty:
                pass

        try:
            jobid = self._queue.get(True, 10)
            self._queue.task_done()
            if jobid is not None:
                with self._r_lock:
                    self._mjob_count += 1
            return jobid, 1
        except Queue.Empty:
            pass

        try:
            jobid = self.job_queue3.get_nowait()
            self.job_queue3.task_done()
            return jobid, False
        except Queue.Empty:
            pass

        return self._get_job()

    def _dec_worker(self):
        with self._r_lock:
            self._work_count -= 1
            if self._work_count == 0:
                self._end_mark = 1

    def run(self):
        self._start_datetime = datetime.datetime.now()
        self._threads = []
        self.cur_jobid = 0
        self._end_mark = 0
        self._work_count = 0

        self._job_count = 0
        self._mjob_count = 0
        self._mjob_all = '?'

        # 日志报告 udp查看
        self._reporter = threading.Thread(target=self.report)
        self._reporter.start()

        # 任务分发
        self._dispatcher = threading.Thread(target=self.do_dispatcher, args=(self._queue, ))
        self._dispatcher.start()

        for i in range(0, self._thread_cnt):
            t = threading.Thread(target=self._job_runner, args=(i, ))
            t.start()

            self._threads.append(t)

        self.wait_run(True)

    def wait_q(self):
        lt = 0
        while True:
            while not self._queue.empty() or not self.job_queue2.empty() or not self.job_queue3.empty():
                self._queue.join()
                self.job_queue2.join()
                self.job_queue3.join()
            if time.time() < lt + 1 and self._running_count==0:
                return True
            time.sleep(2)
            lt = time.time()

    def wait_run(self, report=False):
        for t in self._threads:
            t.join()

        self._dispatcher.join()
        self._end_mark = 1
        self._reporter.join()
        self._dispatcher = None
        self._reporter = None
        self._end_mark = 0
        self._threads = []

        if report:
            end_time = datetime.datetime.now()
            time_span = str(end_time - self._start_datetime)
            report_str = "prog:%s\nlast job is %s\nDONE time used:%s\n" % (' '.join(sys.argv), str(self.cur_jobid), time_span)
            report_str += "mj: %d " % (self._mjob_count)
            sys.stderr.write(report_str)
            self.end_operation({"msg": report_str})

    def end_operation(self, msg):
        pass

    def report(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while 1:
            time.sleep(2)
            prog = "mj:%d/%s\n wc:%d \n rc:%d" % (self._mjob_count, self._mjob_all, self._work_count, self._running_count)
            if isinstance(self.cur_jobid, dict) and 'url' in self.cur_jobid:
                cjstr = utf8str(self.cur_jobid['url'])
            else:
                cjstr = utf8str(self.cur_jobid)

            if len(cjstr) > 200:
                cjstr = cjstr[:200]

            msg = "[pid=%d]job:%s prog:%s\n" % (os.getpid(), cjstr, prog)
            try:
                s.sendto(msg, ("127.0.0.1", self._log_port))

            except Exception as e:
                pass

            if self._end_mark:
                msg = "[pid=%d] DONE\n" % (os.getpid())
                try:
                    s.sendto(msg, ("127.0.0.1", self._log_port))
                except:
                    pass

                return

    def load_ini_file(self, filepath):
        parser = ConfigParser()
        f = open(filepath,'rb')
        parser.readfp(f)

        f.close()
        return parser

    def fetch_option_value(self, parser, common_section, spec_section, option):
        if not parser.has_option(spec_section, option):
            return parser.get(common_section, option)
        else:
            return parser.get(spec_section, option)


    def init_email(self, section="spider_part"):
        email_conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../conf/email_conf.ini")
        send_user_name = None
        send_user_pwd = None
        smtp_host = None
        smtp_port = 465

        common_section = "common"

        parser = self.load_ini_file(email_conf)

        if not parser.has_section(section):
            raise Exception("section: %s not exists in file : %s" % (section, email_conf))

        send_user_name = self.fetch_option_value(parser, common_section, section, "send_user_name")
        send_user_pwd = self.fetch_option_value(parser, common_section, section, "send_user_pwd")
        smtp_host = self.fetch_option_value(parser, common_section, section, "smtp_host")
        smtp_port = int(self.fetch_option_value(parser, common_section, section, "smtp_port"))

        receive_users = self.fetch_option_value(parser, common_section, section, "receive_users").split(";")

        self.Default_EMAIL_RECEIVER = receive_users

        if not send_user_name or not send_user_pwd:
            raise EmailInitException("need send_user_name and send_user_pwd")

        return EmailHelper(send_user_name, send_user_pwd, smtp_host, smtp_port)

    def conf_parse(self, line):
        return line.split("=")[1].strip()

if __name__ == '__main__':
    c = BaseTask("123")
    c.init_email()


