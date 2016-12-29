#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'

from spiders.base.base import BaseTask
from util import mail


class BasicExport(BaseTask):
    def __init__(self, task_name, query=None, thread_cnt=1):
        BaseTask.__init__(self, task_name=task_name, thread_cnt=thread_cnt)
        self.query = query
        self.file_path = None
        self.mail_helper = self.init_email(section="export_part")

    def end_operation(self, msg):
        reader = open(self.file_path, "rb")

        self.mail_helper.send_email_attach(self.Default_EMAIL_RECEIVER, self.task_name, "===export data===", {"%s.csv" % self.task_name: reader})


