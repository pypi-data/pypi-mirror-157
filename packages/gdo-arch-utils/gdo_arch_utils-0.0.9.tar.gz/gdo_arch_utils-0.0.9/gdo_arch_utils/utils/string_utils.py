from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()

class StringUtils:

	@staticmethod
	def split_k_v_str_get_appended_tuple(copy_string_list, key_value_str, entries_sep = ',', key_val_sep = '|'):
		for column_name_value in key_value_str.split(entries_sep):
			items = column_name_value.split(key_val_sep)
			if len(copy_string_list) == len(items) and '' not in items:
				for i in range(len(items)):
					copy_string_list[i] = items[i] + "," + copy_string_list[i]

		return tuple(copy_string_list)

