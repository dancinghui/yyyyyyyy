#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'
from email.mime.text import MIMEText
from email.header import Header
from email import MIMEMultipart, MIMEBase, Encoders
import re
import smtplib


class EmailHelper(object):

    def __init__(self, username, password, smtphost="smtp.exmail.qq.com", smtpport=465):
        self.username = username
        self.password = password
        self.smtphost = smtphost
        self.smtpport = smtpport

        self.server = self.init()

    def __del__(self):
        self.server.close()

    def init(self):
        s = smtplib.SMTP_SSL(self.smtphost, self.smtpport)
        s.login(self.username, self.password)
        return s

    def send_email(self, email, title, message, readers=None):

        if readers:
            return self.send_email_attach(email, title, message, readers)

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

    def send_email_attach(self, email, title, msg, readers_map):

        assert isinstance(readers_map, dict)

        # 构造MIMEMultipart对象做为根容器
        main_msg = MIMEMultipart.MIMEMultipart()

        # 构造MIMEText对象做为邮件显示内容并附加到根容器
        text_msg = MIMEText(msg, 'plain', 'utf-8')
        main_msg.attach(text_msg)

        # 构造MIMEBase对象做为文件附件内容并附加到根容器
        contype = 'application/octet-stream'
        maintype, subtype = contype.split('/', 1)

        for name, reader in readers_map.items():

            data = reader.read()

            if not data:
                try:
                    data = reader.getvalue()
                except Exception:
                    pass

            if not data:
                print "the attach : %s ,content empty" % name
                continue

            file_msg = MIMEBase.MIMEBase(maintype, subtype)

            file_msg.set_payload(data)
            try:
                reader.close()
            except:
                pass

            Encoders.encode_base64(file_msg)

            file_msg.add_header('Content-Disposition', 'attachment', filename = name)
            main_msg.attach(file_msg)

        main_msg['From'] = self.username
        if isinstance(email, list):
            main_msg['To'] = '; '.join(email)
            tolist = email
        else:
            main_msg['To'] = email
            tolist = [email]
        main_msg['Subject'] = Header(title, 'utf-8')

        # 得到格式化后的完整文本
        fullText = main_msg.as_string()
        # 用smtp发送邮件
        print "sending mail to", tolist
        self.server.sendmail(self.username, tolist, fullText)


if __name__ == '__main__':
    email = EmailHelper("jianghao@91htw.com", "Gh853211")
    from StringIO import StringIO
    c = StringIO()
    c.write("this is a attach test")
    c.flush()
    print c.read()
    email.send_email_attach("jianghao@91htw.com", "1234", "just for test", {"attach": c})

