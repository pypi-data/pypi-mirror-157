from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class BoolUtils:
	"""Boolean utilities class"""

	@staticmethod
	def str_to_bool(input_str):
		"""Returns boolean True for any case value of true else False"""
		return input_str.lower() == 'true'
