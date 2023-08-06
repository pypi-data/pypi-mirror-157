#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-09-06 15:52:46
# @Author  : wangmian05
# @Link    : wangmian05@countrygraden.com.cn
# @Version : $Id$
import os
import sys
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from wmfwk.util.config import config, env_prefix
from wmfwk.util import logger as log

encoding = "utf-8"
subject = "算法排布运行错误"


def sendMail(message, attach_content=None, _subject=subject, _to_users=None, _project_name=None, _creator=None):
    """发送邮件"""

    try:
        receivers = config.get("mail.to.users")
        if receivers is not None:
            receivers = str.split(receivers, ",")

        if _to_users is None:
            _to_users = receivers
        if _to_users is None:
            log.warning("接收人为空,不再发送邮件...")
            return
        if message is None:
            log.warning("邮件发送内容为空")
            return

        mail_sender = config.get("mail.user")
        if mail_sender is None:
            log.info("配置获取为空,不在发送邮件")
            return
        mail_passwd = config.get("mail.passwd")
        mail_host = config.get("mail.host")
        mail_port = config.get("mail.port")
        if env_prefix == "dev":
            _subject = "[开发环境]-" + _subject
        if env_prefix == "uat":
            _subject = "[测试环境]-" + _subject
        if env_prefix == "prod":
            _subject = "[生产环境]-" + _subject
        smtpObj = smtplib.SMTP(mail_host, mail_port)
        smtpObj.starttls()
        smtpObj.login(mail_sender, mail_passwd)
        _msg = "<h3>智能地库算法排布运行错误</h3>"
        if _project_name:
            _msg = _msg + "<p>项目名称:  <b>" + _project_name + "</b></p>"
        if _creator:
            _msg = _msg + "<p>创建人:  <b>" + _creator + "</b></p>"
        if message:
            _msg = _msg + "<p>  " + message + "</p>"

        # 创建一个带附件的实例
        message = MIMEMultipart()
        message.attach(MIMEText(_msg, "html", encoding))
        if attach_content:
            # 构造附件1，传送当前目录下的 test.txt 文件
            attach_file = open('error.json', 'wb+')
            file_cont = str.encode(attach_content, encoding)
            attach_file.write(file_cont)
            attach_file.close()
            att1 = MIMEText(file_cont, 'base64', encoding)
            att1["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            att1["Content-Disposition"] = 'attachment; filename="error.json"'
            message.attach(att1)

        message["From"] = Header("智能地库", encoding)
        message["To"] = Header("智能地库管理员", encoding)
        message["Subject"] = Header(_subject, encoding)
        smtpObj.sendmail(mail_sender, _to_users, message.as_string())
        os.remove('error.json')
        log.info("邮件发送成功...")
    except:
        log.error("邮件发送失败:{}", sys.exc_info())


if __name__ == "__main__":
    sendMail("我也不知道啥错误...", "{\"building\": [[[92356, -81123], [92356, -88623]]]}")
    print("证明邮件发送是异步发送的")
