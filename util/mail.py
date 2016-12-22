#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'
from email.mime.text import MIMEText
from email.header import Header
import re
import smtplib


class EmailHelper(object):
    def __init__(self, username, password, smtphost="smtp.exmail.qq.com", smtpport=465):
        self.username = username
        self.password = password
        self.smtphost = smtphost
        self.smtpport = smtpport

        self.server = self.init()

    def init(self):
        s = smtplib.SMTP_SSL(self.smtphost, self.smtpport)
        s.login(self.username, self.password)
        return s

    def send_email(self, email, title, message):

        if isinstance(message, unicode):
            message = message.encode('utf-8')
        if isinstance(title, unicode):
            title = message.encode('utf-8')

        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = Header(title, 'utf-8')
        msg['From'] = self.username

        if isinstance(email, list):
            msg['To'] = '; '.join(email)
            tolist = email
        else:
            msg['To'] = email
            tolist = [email]

        for i in range(0, len(tolist)):
            m = re.search('<([a-z0-9_@\-.]*)>\s*$', tolist[i], re.I)
            if m:
                tolist[i] = m.group(1)

        print "sending mail to", tolist
        print msg.as_string()

        self.server.sendmail(self.username, tolist, msg.as_string())


if __name__ == '__main__':
    email = EmailHelper("jianghao@91htw.com", "Gh853211")
    email.send_email("jianghao@91htw.com", "test", "test")

