from enum import Enum
from typing import List
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class ListCase(Enum):
	Upper = 'upper'
	Lower = 'lower'
	Default = 'default'


class BlankListError(IndexError):
	"""Occurs when there's no element in the list"""

	def __init__(self, message):
		self.message = message
		super().__init__(self, self.message)


class ListUtils:

	@staticmethod
	def list_to_str_sep_delimiter(input_list, delimiter):
		return delimiter.join(input_list)

	@staticmethod
	def replace_list_items_with_custom_mapping_from_dict(mapping_dict, list_to_replace):
		return [item if item not in mapping_dict else mapping_dict[item]
			for item in list_to_replace]

	@staticmethod
	def add_prefix_suffix_to_items_in_list(input_list: List[str], prefix = '', suffix = ''):
		"""
			Concept used : Python list comprehension

			This method takes prefix and suffix.
			Which ever value is passed would be applied to each item in the list or a combination
			of both.
		"""
		result = [f"{prefix}{item}{suffix}" for item in input_list]
		logger.debug(f"add_prefix_suffix_to_items_in_list {result=}")
		return result

	@staticmethod
	def get_chunked_sub_lists(original_list, chunk_size):
		return [original_list[index:index + chunk_size] for index in
			range(0, len(original_list), chunk_size)]

	@staticmethod
	def is_empty(original_list: List) -> bool:
		"""Return bool value True if list is empty"""
		try:
			original_list[0]
		except BlankListError as be:
			return True
		return False

	@staticmethod
	def raise_exception_on_empty(original_list: List):
		"""Raise exception if list is empty"""
		try:
			original_list[0]
		except IndexError as ie:
			raise BlankListError("No element found in list") from ie

	@staticmethod
	def is_list_element_present_in_str(original_list, search_str):
		logger.debug(f"Searching str {search_str}")
		return any(item in search_str for item in original_list)

	@staticmethod
	def is_tuple_list_element_matches_search_tuple(original_list, search_tuple):
		"""

		Matches search_tuple 1st item if it's present in original list zipped first item. Doesn't
		look for exact match.
		search_tuple index 0 can be superset of index 0 of original list.
		2nd item should be an exact match.
		Example:-
		1) True case
		original_list=[('SFMC_Bounces_20220411', 'cp_aed'), ('SFMC_Bounces_20220411', 'cp_ap'),
		('SFMC_Bounces_20220411', 'cp_eu'), ('SFMC_Bounces_20220411', 'cp_la'),
		('SFMC_Bounces_20220411', 'cp_na'), ('SFMC_Bounces_20220411', 'cp_sh_eltamd'),
		('SFMC_Bounces_20220411', 'toms'), ('SFMC_Bounces_20220411', 'hills')]
		search_tuple=('cp_aed/landing/2022/04/11/SFMC_Bounces_20220411.csv', 'cp_aed')

		2) False case
		original_list=[('SFMC_Bounces_20220411.parquet', 'cp_aed'), ('SFMC_Bounces_20220411',
		'cp_ap'), ('SFMC_Bounces_20220411', 'cp_eu'), ('SFMC_Bounces_20220411', 'cp_la'),
		('SFMC_Bounces_20220411', 'cp_na'), ('SFMC_Bounces_20220411', 'cp_sh_eltamd'),
		('SFMC_Bounces_20220411', 'toms'), ('SFMC_Bounces_20220411', 'hills')]
		search_tuple=('cp_aed/landing/2022/04/11/SFMC_Bounces_20220411.csv', 'cp_aed')

		"""

		logger.info(f"Searching tuple {search_tuple}")
		return any(
			(tuple_item1, tuple_item2) for tuple_item1, tuple_item2 in original_list if
				search_tuple[1] == tuple_item2 and tuple_item1 in search_tuple[0]
		)

	@staticmethod
	def replace_items_in_list_or_change_case(
		input_list: List[str], replace_str = '', replace_with_str = '',
		case = ListCase.Default
	):
		"""
		Concept used : Python list comprehension

		This method takes
		@replace_str : str to replace with default value ''
		@replace_with_str : str to replace with default value ''

		If these values are not passed the method can be used just to change the case of the list
		to upper or lower
		@case : restricted by ListCase enum which accepts only 3 values default case
		"""
		return [
			col.replace(replace_str, replace_with_str).lower() if case == ListCase.Lower
			else col.replace(replace_str, replace_with_str).upper() if case == ListCase.Upper
			else col.replace(replace_str, replace_with_str)
			for col in input_list
		]
