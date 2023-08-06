from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class DictUtils:
	@staticmethod
	def gen_dict_key_from_dict1_value_from_dict2(dict1, dict2):
		"""
			Concept used : Python dictionary comprehension

			This method generates a map with keys from dict1 and value from dict2
			if value in dict1 matches key in dict2 skips other keys from dict1
			Example:
			dict1 = {"Col1":"col1","Col2":"col2","Col6":"col6"}
			dict2 = {"col1":"Col_1","col2":"Col_2","col7":"Col_7"}
			result_dict = {"Col1":"Col_1","Col2":"Col_2"}
		"""


		return {
			key: dict2.get(value, value)
			for key, value in dict1.items()
			if value in dict2.keys()
		}
