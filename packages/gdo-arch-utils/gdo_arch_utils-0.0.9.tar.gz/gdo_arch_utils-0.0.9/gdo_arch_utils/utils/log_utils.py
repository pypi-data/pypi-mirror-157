from os import environ
from sys import stdout
from loguru import logger


class LogUtils:
	@staticmethod
	def get_logger():
		level = environ.get('LOG_LEVEL') or 'INFO'
		log_format_str = environ.get('LOG_FORMAT_STR') or '{level} - {message}'
		logger.remove()
		logger.add(stdout, format = log_format_str, level = level)
		return logger
