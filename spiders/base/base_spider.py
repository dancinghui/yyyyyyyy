#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base import BaseTask
from util.mail import EmailHelper
from exepts.emailException import EmailInitException
from spiders.base.httpreq import SpeedControlRequests, SessionRequests
from spiders.base.runtime import Log
from spiders.base.exceptions import AccountErrors, LoginErrors, SpiderErrors
import os
import time
import abc
import threading


class BaseSpider(BaseTask, SpeedControlRequests):

    Default_EMAIL_RECEIVER = ["jianghao@91htw.com"]

    def __init__(self, spider_name, queue_size=200, thread_cnt=10):
        BaseTask.__init__(self, spider_name, queue_size, thread_cnt)
        SpeedControlRequests.__init__(self)

        self.session_request = SessionRequests()
        self.email_helper = self.init_email()
        self.filters = []

    def init_email(self):
        email_conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../conf/email.conf")
        send_user_name = None
        send_user_pwd = None
        smtp_host = "smtp.exmail.qq.com"
        smtp_port = 465

        with open(email_conf, "rb") as f:
            for line in f:
                if "send_user_name" in line:
                    send_user_name = self.conf_parse(line)
                    continue
                if "send_user_pwd" in line:
                    send_user_pwd = self.conf_parse(line)
                    continue
                if "smtp_host" in line:
                    smtp_host = self.conf_parse(line)
                    continue
                if "smtp_port" in line:
                    smtp_port = self.conf_parse(line)
                    continue

                if "receive_users" in line:
                    for e in self.conf_parse(line).split(";"):
                        BaseSpider.Default_EMAIL_RECEIVER.append(e.strip())

        if not send_user_name or not send_user_pwd:
            raise EmailInitException("need send_user_name and send_user_pwd")

        return EmailHelper(send_user_name, send_user_pwd, smtp_host, smtp_port)

    def conf_parse(self, line):
        return line.split("=")[1].strip()

    def end_operation(self, msg):
        if "msg" in msg:
            self.email_helper.send_email(BaseSpider.Default_EMAIL_RECEIVER, self.task_name, msg["msg"])

    def dispatcher(self, q):
        for i in range(100):
            q.put(i)

    def run_job(self, job):
        print job

    def re_add_job(self, job):
        self.job_queue3.put(job)

    def saveItems(self, items):
        for item in items:
            item = self.do_filter(item)
            if item:
                item.insert()

    def do_filter(self, item):

        for filter in self.filters:
            item = filter.run(item)

        return item


class LimitedResource(object):
    def __init__(self, lst, shared):
        self.res = []
        self.reslock = []
        for i in lst:
            self.res.append(i)
            self.reslock.append(0)

        self.idx = 0
        self.locker = threading.RLock()
        self._shared = shared


    def get(self, checker):
        with self.locker:
            for nnn in range(len(self.res)+1):
                if not self.reslock[self.idx] and checker(self.res[self.idx]):
                    if not self._shared:
                        self.reslock[self.idx] = 1
                    rv = self.res[self.idx]
                    self.idx = (self.idx + 1) % len(self.res)
                    return rv

                self.idx = (self.idx + 1) % len(self.res)

        raise AccountErrors.NoAccountError("no more account")

    def unlock(self, obj):
        if self._shared:
            return
        with self.locker:
            for nnn in range(len(self.res) + 1):
                if self.res[nnn] is obj:
                    self.reslock[nnn] = False
                    return True

        raise RuntimeError('no such object')

class ShareLimitedResource(LimitedResource):

    res = []
    reslock = []
    locker = threading.RLock()

    def __init__(self, lst, shared):
        for i in lst:
            self.res.append(i)
            self.reslock.append(0)
        self.idx = 0
        self._shared = shared





class MultiRequestsWithLogin(SessionRequests):
    def __init__(self, ac):
        SessionRequests.__init__(self)
        self.account = ac
        self.islogin = False
        self.req_count = 0
        self.isvalid = True
        self.select_user_agent('firefox')

    def set_nologin(self):
        with self.locker:
            self.islogin = 0
            self.reset_session()

    def _inc_call(self):
        with self.locker:
            self.req_count += 1
            return self.req_count

    def _dec_call(self):
        with self.locker:
            self.req_count -= 1
            return self.req_count

    def do_login(self):
        with self.locker:
            while self.req_count != 0:
                self.locker.release()
                time.sleep(1)
                self.locker.acquire()

            # now no one is req...
            first_loop = True
            while not self.islogin:
                if not self.is_valid():
                    break
                if not first_loop:
                    Log.warning("login failed, sleep 5s")
                    time.sleep(5)
                first_loop = False
                self.islogin = self._real_do_login()
            return self.islogin

    def is_valid(self):
        """检查帐号是否被封,没有被封返回True"""
        return self.isvalid

    @abc.abstractmethod
    def _real_do_login(self):
        raise NotImplementedError()

    def need_login(self, url, con, hint):
        """检查一个网络文件内容是否需要登录，必要时抛出LoginErrors里的异常"""
        pass


class MRLManager(object):
    def __init__(self, accounts, req_class, shared=False):
        assert isinstance(accounts, list)
        net_list = []
        for i in accounts:
            lp = req_class(i)
            if not isinstance(lp, MultiRequestsWithLogin):
                raise RuntimeError("initial this class with req_class = <sub class of MultiRequestsWithLogin>")
            net_list.append(lp)

        self.net_list = LimitedResource(net_list, shared)
        self._nettls = threading.local()


    def ensure_login_do(self, prechecker, caller, checker, trylimit=-1):
        """caller 调用具体函数，得到的返回值会交给checker处理，checker在必要时抛出LoginErrors里的异常"""

        retry_cnt = 0
        while retry_cnt != trylimit:
            retry_cnt += 1

            net = getattr(self._nettls, 'net', None)
            while net is None:
                net1 = self.net_list.get(lambda v: v.is_valid())
                net1.do_login()
                if net1.is_valid():
                    setattr(self._nettls, 'net', net1)
                    net = net1

            net._inc_call()

            try:
                if prechecker is not None:
                    prechecker(net)
                con = caller(net)
                if checker is not None and con is not None:
                    checker(net, con)

                net._dec_call()
                return con

            except LoginErrors.RetryError:
                net._dec_call()
                time.sleep(5)
            except(LoginErrors.AccountHoldError, SpiderErrors.FatalError):
                net.set_nologin()
                net._dec_call()
                setattr(self._nettls, 'net', None)
                self.net_list.unlock(net)
                time.sleep(5)

            except LoginErrors.NeedLoginError:
                net.set_nologin()
                net._dec_call()
                net.do_login()
                if not net.is_valid():
                    setattr(self._nettls, 'net', None)
                    self.net_list.unlock(net)
                time.sleep(5)

            except Exception:
                net._dec_call()
                raise

        return None

    def el_request(self, url, hint=None, prechecker=None, checker=None, **kwargs):
        caller = lambda net: net.request_url(url, **kwargs)
        if checker is None:
            checker = lambda net,con : net.need_login(url, con, hint)
        return self.ensure_login_do(prechecker, caller, checker)

    def set_nologin(self):
        net = getattr(self._nettls, 'net', None)
        if net is None:
            return
        if net.req_count > 0:
            Log.error('invalid function call!!')
            return

        net.set_nologin()
        setattr(self._nettls, 'net', None)
        self.net_list.unlock(net)

    def cur_worker(self):
        return getattr(self._nettls, 'net', None)

    def release_obj(self):
        net = getattr(self._nettls, 'net', None)
        if net is None:
            return
        if net.req_count > 0:
            Log.error("invalid function call!!")
            return
        setattr(self._nettls, 'net', None)
        self.net_list.unlock(net)


class ShareMRLManager(MRLManager):
    def __init__(self, accounts, req_class, shared=False):
        assert isinstance(accounts, list)
        net_list = []
        for i in accounts:
            lp = req_class(i)
            if not isinstance(lp, MultiRequestsWithLogin):
                raise RuntimeError("initial this class with req_class = <sub class of MultiRequestsWithLogin>")
            net_list.append(lp)
        self.net_list = ShareLimitedResource(net_list, shared)
        self._nettls = threading.local()





if __name__ == '__main__':
    s = BaseSpider("testspider", thread_cnt=2)
    s.run()