from datetime import datetime
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class DateUtils:
	@staticmethod
	def str_as_date(date_str, format_str):
		return datetime.strptime(date_str, format_str).date()

	def str_as_date_Ymd(date_str):
		"""Expects the date_str in format %Y-%m-%d """
		return datetime.strptime(date_str, "%Y-%m-%d").date()
