'''
***************
Name:Sunny
Time:2020/3/7
***************
'''
'''
qq邮箱：smtp.qq.com  端口：465
163邮箱：smtp.163.com  端口：465

QQ邮箱账号:418040021@qq.com
smtp服务授权码:yqrsvrauiwaybhdi

'''
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from common.handlepath import report_dir
from common.handleconfig import conf


class SendEmail(object):

    @staticmethod
    def send_email(reportname,title):
        '''
        发送测试报告邮件
        :param reportname: 报告名称
        :param title: 邮件主题
        :return:
        '''
        # 连接smtp服务器
        smtp = smtplib.SMTP_SSL(host=conf.get("email","host"),port=conf.getint("email","port"))
        smtp.login(user=conf.get("email","user"),password=conf.get("email","pwd"))
        # 构建一封邮件
        # 读取邮件报告的内容
        with open(os.path.join(reports_dir,"report.html"),"rb") as f:
            content = f.read()
        # 创建一个多组件对象
        msg = MIMEMultipart()
        # 邮件内容
        text_msg = MIMEText(content,_subtype="html",_charset="utf8")
        # 将邮件加入到组件
        msg.attach(text_msg)
        # 添加附件内容
        report_msg = MIMEApplication(content)
        # 添加附件头内容
        report_msg.add_header('content-disposition', 'attachment', filename=reportname)
        # 将附件添加到组件中
        msg.attach(report_msg)

        msg["Subject"] = title
        msg["From"] = conf.get("email","from_addr")
        msg["To"] = conf.get("email","to_addr")
        # 发送邮件
        smtp.send_message(msg,from_addr=conf.get("email","from_addr"),to_addrs=conf.get("email","to_addr").split(","))

if __name__ == "__main__":
    file_path = os.path.join(reports_dir,"report.html")
    reportname = file_path.split("\\")[-1]
    SendEmail.send_email(reportname,"多人发送试一下")

