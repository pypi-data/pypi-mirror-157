# -*- coding: utf-8 -*-
# @Time    : 2020/8/12 16:24
# @Author  : SongWei

import base64
import os
import smtplib
import time
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import paramiko
import requests
from gblib.gb_common import GbConfig
from gblib.gb_log import LogManager
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment, FileContent, FileName, Disposition
from sendgrid.helpers.mail import Mail

config = GbConfig()

logger = LogManager('email', log_level='INFO').getLogger_and_addSingleFileHandler(config.get('EMAIL', 'LOG_PATH'))


def send_email_with_big_attachment(title, msg_text, receiver, nick_name=None, attachment=None):
	# 发送大文件时仍然使用腾讯企业邮
	from_addr = 'qvdingcheng@gamebeartech.com'
	password = 'SDfGKcMF9AfUaNNC'
	smtp_server = 'smtp.exmail.qq.com'

	msg = MIMEMultipart()
	msg['From'] = Header(config.get('EMAIL', 'FROM_EMAIL'), 'utf-8')
	msg['Subject'] = Header(title, 'utf-8')
	msg.attach(MIMEText(msg_text, _charset='utf-8'))
	part = MIMEApplication(open(attachment, 'rb').read())
	part['Content-Type'] = 'application/octet-stream'
	part.add_header('Content-Disposition', 'attachment', filename=attachment)
	msg.attach(part)
	try:
		server = smtplib.SMTP(smtp_server, 587)
		server.set_debuglevel(1)
		server.starttls()
		server.login(from_addr, password)
		server.sendmail(from_addr, receiver, msg.as_string())
		server.quit()
		if os.path.splitext(attachment)[1] == '.7z':
			os.system('rm -rf {}'.format(attachment))
	except smtplib.SMTPException:
		return False
	return True


def send_email(title, msg_text, receiver, nick_name=None, attachment=None, html_content=False):
	"""
	:param title: 邮件标题
	:param msg_text: 邮件正文
	:param receiver: list类型，收件人列表，一个人也要写成列表
	:param nick_name: 兼容字段，避免修改历史的代码，现在不需要，可以不填
	:param attachment: 附件路径
	:param html_content: 默认为文本格式，设为True则改为html格式
	:return: True or False
	"""
	if isinstance(receiver, str):
		receiver = [receiver]
	logger.info('----------------------------------------------------------------------------------------------------------------')
	logger.info(' -- '.join([title, msg_text, ','.join(receiver), str(attachment)]))
	if attachment:
		if not os.path.exists(attachment):
			return False
	if html_content:
		message = Mail(from_email=config.get('EMAIL', 'FROM_EMAIL'), to_emails=receiver, subject=title, html_content=msg_text)
	else:
		message = Mail(from_email=config.get('EMAIL', 'FROM_EMAIL'), to_emails=receiver, subject=title, plain_text_content=msg_text)

	try:
		if attachment:
			if os.path.getsize(attachment) / (1024 * 1024) > 18:  # 如果附件大于18M，使用7z压缩
				filepath = os.path.splitext(attachment)[0]
				zip_path = filepath + '.7z'
				# centos下压缩7z的命令是7za，ubuntu下是7zr，需要在/url/bin下手动创建一个7za软连接指向7zr
				os.system('7za a {} {} > /dev/null'.format(zip_path, attachment))
				attachment = zip_path
			else:  # sendgrid正文加附件一共不能超过20M
				f = open(attachment, 'rb')
				data = f.read()
				encoded = base64.b64encode(data).decode()
				f.close()
				if os.path.splitext(attachment)[1] == '.7z':
					os.system('rm -rf {}'.format(attachment))
				att = Attachment()
				att.file_content = FileContent(encoded)
				att.file_name = FileName(os.path.split(attachment)[-1])
				att.disposition = Disposition('attachment')
				message.attachment = att
	except Exception as err:
		logger.error('7z file failed: attachment: {} err: {}'.format(attachment, err))

	for i in range(int(config.get('EMAIL', 'EMAIL_RETRY_TIMES')) + 1):  # 如果发送失败则重传
		try:
			if attachment and os.path.getsize(attachment) / (1024 * 1024) > 18:  # 如果压缩后仍然大于18M，采用企业邮箱方式发送
				logger.info('use enterprise mailbox... ' + 'RETRY_TIMES: ' + str(i))
				send_email_with_big_attachment(title, msg_text, receiver, nick_name, attachment)
			else:
				sendgrid_client = SendGridAPIClient(config.get("EMAIL", "API_KEY"))
				sendgrid_client.send(message)
			break
		except Exception as err:
			logger.error('send email failed: ' + str(err) + '[{}]Retry...'.format(i))
			time.sleep(int(config.get('EMAIL', 'EMAIL_RETRY_INTERVAL_TIME')))
	return True


def send_email_of_html_table(title: str, receiver: str, tables_list: list, attachment=None):
	"""
	发送html表格的邮件
	:param title: 邮件标题
	:param receiver: 邮件接收者
	:param tables_list: 1个或多个表格，每个表格是list的一个元素，每个元素是一个字典
		例如：[
			{
				'header': 'Main Language result',
				'data': [
					{'a': 1, 'b': 2, 'c': 3}, {'a': 4, 'b': 5, 'c': 6}
				],
				'columns': ['a', 'b', 'c']
			},
		]
	:param attachment: 附件地址
	:return: bool
	"""
	h4 = '<h4>{0}</h4>'
	table_str = '<table style="top: 0;font-family: verdana,arial,sans-serif;font-size:11px;color:#333333;border-width: 1px;border-color: #666666;border-collapse: collapse;">{0}{1}</table>'
	th = '<th style="border-width: 1px;padding: 8px;border-style: solid;border-color: #666666;background-color: #dedede;">{0}</th>'
	td = '<td style="border-width: 1px;padding: 8px;border-style: solid;color:{0};border-color: #666666;background-color: #ffffff;">{1}</td>'

	body_str = ''
	for tb in tables_list:
		# h4 block
		header = h4.format(tb['header'])

		# div th blcok
		th_str = ''.join([th.format(x) for x in tb['columns']])
		div_th = '<tr>{0}</tr>'.format(th_str)

		div_td = ''
		try:
			for line in tb['data']:
				div_td += '<tr>'
				color_bl = line.get('important', False)
				if color_bl:
					color = '#ff0000'
				else:
					color = '#333333'

				for col in tb['columns']:
					div_td += td.format(color, line.get(col))
				div_td += '</tr>'
		except Exception as err:
			print("send email error: {}, table: {}".format(err, tables_list))
			raise Exception("error: {}, table format error".format(err))

		body_str += header + table_str.format(div_th, div_td)

	email_html = """
		<html>
			<head>
				<title></title>
			</head>

			<body>
				{0}
			</body>
		</html>
	""".format(body_str)

	return send_email(title, email_html, receiver, attachment, html_content=True)


def ssh_scp_get(ip, port, user, password, remote_file, local_file):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip, port, user, password)
	paramiko.SFTPClient.from_transport(ssh.get_transport())
	sftp = ssh.open_sftp()
	sftp.get(remote_file, local_file)


def ssh_scp_put(ip, port, user, password, local_file, remote_file):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip, port, user, password)
	paramiko.SFTPClient.from_transport(ssh.get_transport())
	sftp = ssh.open_sftp()
	sftp.put(local_file, remote_file)


def http_get(url):
	response = requests.get(url)
	return response.text


def http_post(url, json_dict):
	r = requests.post(url, json_dict)
	return r.text
