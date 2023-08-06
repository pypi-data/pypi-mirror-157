# -*- coding: utf-8 -*-
# @Time    : 2020/8/12 17:36
# @Author  : SongWei

import logging
import os
import re
import sys
import time
from abc import ABC, abstractmethod

from gblib.gb_common import GbConfig

config = GbConfig()


class LogManager(object):
	def __init__(self, logger_name, log_level=None):
		self.logger = logging.getLogger(logger_name)
		self.logger.setLevel(config.get('BASIC', 'LOG_LEVEL'))
		if log_level:
			self.logger.setLevel(log_level)  # 默认读取config中的level，用户初始化后设为初始化等级

	def addHandler(self, *handlers):
		for handler in handlers:
			self.logger.addHandler(handler.get_handler())

	def getLogger(self):
		return self.logger

	def getLogger_and_addAllHandler(self, log_dir=None):
		self.addHandler(FileErrorHandler(log_dir), FileInfoHandler(log_dir), ConsoleHandler())
		return self.logger

	def getLogger_and_addConsoleHandler(self, colorful=False):
		self.addHandler(ConsoleHandler(colorful))
		return self.logger

	def getLogger_and_addFileHandler(self, log_dir=None):
		"""
		logs seperate by date
		:param log_dir:
		:return:
		"""
		self.addHandler(FileInfoHandler(log_dir), FileErrorHandler(log_dir))
		return self.logger

	def getLogger_and_addSingleFileHandler(self, log_dir):
		"""
		usually use this handler
		:param log_dir:
		:return:
		"""
		self.addHandler(SingleFileHandler(log_dir))
		return self.logger


class LogHandler(ABC):
	def __init__(self):
		# 时间-日志器名称-日志级别-文件名-函数行号-错误内容
		self.format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s  - %(lineno)s - %(message)s')

	def set_log_format(self, log_format):
		self.format = logging.Formatter(log_format)

	@abstractmethod
	def get_handler(self):
		pass


class FileInfoHandler(LogHandler):
	def __init__(self, log_dir=None):
		self.time_str = time.strftime('%Y%m%d', time.localtime(time.time()))
		super().__init__()
		self.log_dir = log_dir or config.get('BASIC', 'LOG_DIR')
		self.log_dir = os.path.join(self.log_dir, 'info')
		if not os.path.exists(self.log_dir):
			os.makedirs(self.log_dir)

	def get_handler(self):
		info_log_path = os.path.join(self.log_dir, self.time_str + '.log')
		info_handle = logging.FileHandler(info_log_path)
		info_handle.setLevel(logging.INFO)
		info_handle.setFormatter(self.format)
		return info_handle


class FileErrorHandler(LogHandler):
	def __init__(self, log_dir=None):
		self.time_str = time.strftime('%Y%m%d', time.localtime(time.time()))
		super().__init__()
		self.log_dir = log_dir or config.get('BASIC', 'LOG_DIR')
		self.log_dir = os.path.join(self.log_dir, 'error')
		if not os.path.exists(self.log_dir):
			os.makedirs(self.log_dir)

	def get_handler(self):
		error_log_path = os.path.join(self.log_dir, self.time_str + '.log')
		error_handle = logging.FileHandler(error_log_path)
		error_handle.setLevel(logging.ERROR)
		error_handle.setFormatter(self.format)
		return error_handle


class ConsoleHandler(LogHandler):
	def __init__(self, colorful=False):
		super().__init__()
		self.colorful = colorful

	def get_handler(self):
		if self.colorful:
			console_handle = ColorHandler()
		else:
			console_handle = logging.StreamHandler()
		console_handle.setFormatter(self.format)
		return console_handle


class SingleFileHandler(LogHandler):
	def __init__(self, log_path=None):
		super().__init__()
		self.format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		self.log_path = log_path
		directory, file = os.path.split(self.log_path)
		if not re.match(r'^\w+.log$', file):
			raise Exception('log path error, must endswith .log: {}'.format(file))
		if not os.path.exists(directory):
			os.makedirs(self.log_path)

	def get_handler(self):
		email_log_path = self.log_path
		error_handle = logging.FileHandler(email_log_path)
		error_handle.setLevel(logging.DEBUG)
		error_handle.setFormatter(self.format)
		return error_handle


class ColorHandler(logging.Handler):
	"""
	彩色日志
	"""
	terminator = '\n'

	def __init__(self):
		"""
		Initialize the handler.
		If stream is not specified, sys.stderr is used.
		"""
		logging.Handler.__init__(self)
		self.stream = sys.stdout

	def flush(self):
		"""
		Flushes the stream.
		"""
		self.acquire()
		try:
			if self.stream and hasattr(self.stream, "flush"):
				self.stream.flush()
		finally:
			self.release()

	@staticmethod
	def _build_color_msg(record_level, assist_msg, effective_information_msg):
		map_level_color = {
			10: '\033[0;32m{}\033[0m'.format(assist_msg),
			20: '\033[0;36m{}\033[0m'.format(assist_msg),
			30: '\033[0;33m{}\033[0m'.format(assist_msg),
			40: '\033[0;35m{}\033[0m'.format(assist_msg),
			50: '\033[0;31m{}\033[0m'.format(assist_msg)
		}
		msg_color = map_level_color.get(record_level) or '{}  {}'.format(assist_msg, effective_information_msg)
		return msg_color

	def emit(self, record: logging.LogRecord):
		effective_information_msg = record.getMessage()  # 不能用msg字段，例如有的包的日志格式化还有其他字段
		assist_msg = self.format(record)
		msg_color = self._build_color_msg(record.levelno, assist_msg, effective_information_msg)
		self.stream.write(msg_color)
		self.stream.write(self.terminator)
		self.flush()
