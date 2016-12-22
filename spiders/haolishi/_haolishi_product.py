#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base_spider import MultiRequestsWithLogin, BaseSpider
from parsers.haolishi import HaolishiParser

class HaolishiLogin(MultiRequestsWithLogin):
    LOGIN_URL = "http://www.haolishi.cn/user.php?act=login"

    REQUEST_LOGIN_URL = 'http://www.haolishi.cn/user.php?XDEBUG_SESSION_START=ECLIPSE_DBGP'

    def __init__(self, ac):
        MultiRequestsWithLogin.__init__(self, ac)
        self.cansearch = 0


    def is_valid(self):
        return self.isvalid


    def need_login(self, url, con, hint):
        if 'user.php?act=login' in url:
            return True

        return False

    def _real_do_login(self):
        username, password = self.account['u'], self.account['p']

        data = {'username': username, 'password':password, 'act': 'act_login', 'back_act':'user.php', 'submit':'立即登录'}
        headers = {'Referer': HaolishiLogin.LOGIN_URL}
        con = self.request_url(HaolishiLogin.REQUEST_LOGIN_URL, data=data, headers=headers)

        return True


class HaolishiGlobleData(object):
    PAGE_URL = 'http://www.haolishi.cn/category.php?id=39'


class HaolishiSpider(BaseSpider):

    def __init__(self, queue_size=200, thread_cnt=10):
        BaseSpider.__init__(self, 'haolishi', queue_size=queue_size, thread_cnt=thread_cnt)
        self.parser = HaolishiParser(self)

    def dispatcher(self, q):
        self.add_main_job({'url':HaolishiGlobleData.PAGE_URL})

    def run_job(self, job):
        if not job:
            return
        if 'page' in job:
            job['url'] += '&page=%d' % job.get('page')
        resp = self.request_url(job.get('url'))
        if resp:
            items = self.parser.parse(resp.text, job)
            self.saveItems(items)











if __name__ == '__main__':
    # l = HaolishiLogin({'u':'13612729997','p':'123456'})
    # l.do_login()

    s = HaolishiSpider(thread_cnt=1)
    s.run()






