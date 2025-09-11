from email.mime.text import MIMEText
from email.header import Header
import smtplib
from django.conf import settings
from django.http import HttpResponse


# 这是一个调用emailForVerification()函数的例子
def testzjz():
    # 发送的邮件标题
    emailTitle = '测试邮件标题'
    # 发送的邮件内容
    emailContent = '测试邮件内容'
    # 接收方的邮箱
    emailRecipients = []
    emailRecipients.append('1335045869@qq.com')
    emailRecipients.append('1712269587@qq.com')
    result = emailForVerification(emailTitle, emailContent, emailRecipients)
    # return HttpResponse(emailRecipients)
    # return HttpResponse(result)
    return result

# 发送包含验证信息的邮件
def emailForVerification(emailTitle: str, emailContent:str, emailRecipients: list):
    try:
        # 构建邮件
        msg = MIMEText(_text = emailContent, _subtype = 'plain', _charset = 'utf-8')
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = ', '.join(emailRecipients)
        msg['Subject'] = Header(s = emailTitle, charset = 'utf-8')

        # 发送
        server = smtplib.SMTP_SSL(host = settings.EMAIL_HOST, port = settings.EMAIL_PORT)
        server.login(user = settings.EMAIL_HOST_USER, password = settings.EMAIL_HOST_PASSWORD)
        server.sendmail(
            from_addr = settings.EMAIL_HOST_USER,
            to_addrs = emailRecipients,
            msg = msg.as_string()
        )
        server.quit()
        return "发送成功"
    except Exception as e:
        return f"失败: {str(e)}"

