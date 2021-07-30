import json
import os
import smtplib
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from FastApi.common.log import Logger
from FastApi.conf.config import ReadConfig


def create_html_body(case_body):
    html_body = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
    <table align="center" width="80%" bgcolor="#00E3E3" BORDER=3 cellspacing=3>
        <!--页头-->
        <tr align="center" >
            <td>特性名称</td>
            <td>总用例数</td>
            <td>通过数</td>
            <td>失败数</td>
            <td>通过率</td>
            <td>执行时间</td>
        </tr>
        <!--内容-->
        <tr align="center" >''' + case_body + '''</tr>
    </table>
    </body>
    </html>
    '''
    return html_body


class SendMail:
    """邮件发送"""

    def __init__(self):
        self.config = ReadConfig()
        self.log = Logger().logger

    def send_mail(self):
        # 第三方服务
        mail_host = self.config.get_mail('mail_host')  # 设置服务器
        mail_user = self.config.get_mail('mail_user')  # 用户名
        mail_pass = self.config.get_mail('mail_pass')  # 口令

        sender = self.config.get_mail('sender')
        receivers = self.config.get_mail('receiver')

        # 表格html代码
        td = '<td>%s</td>'

        # json日志存放路径
        path = os.path.dirname(__file__)
        log_file = path + '/run/demo.json'

        # 解析json文件
        with open(log_file, 'r', encoding='utf-8') as f:
            summary = json.loads(f.read())['report']['summary']
            passed = summary['passed']
            failed = summary['num_tests'] - summary['passed']
            num_tests = summary['num_tests']
            pass_rate = '{:.2%}'.format(passed / num_tests)
            duration = round(summary['duration'] / 3600, 1)
            demoBody = td % 'demo测试' + td % num_tests + td % passed + td % failed + td % pass_rate + td % duration

        # 邮件正文
        html_body = create_html_body(demoBody)

        message = MIMEMultipart()
        tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        message['Subject'] = Header("接口自动化测试报告" + "_" + tm, 'utf-8')
        message['From'] = Header("本地定时发送", 'utf-8')  # 邮件里展示用户名
        message['To'] = receivers

        message.attach(MIMEText(html_body, 'html', 'utf-8'))

        smtp_obj = smtplib.SMTP()
        smtp_obj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtp_obj.login(mail_user, mail_pass)
        smtp_obj.sendmail(sender, receivers, message.as_string())
        print('邮件发送成功，请查收')
        self.log.info('邮件发送成功')


if __name__ == '__main__':
    mail = SendMail()
    mail.send_mail()
