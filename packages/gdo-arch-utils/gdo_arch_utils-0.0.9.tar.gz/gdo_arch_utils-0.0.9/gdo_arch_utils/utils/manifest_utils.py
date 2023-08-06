from gdo_arch_utils.dto.manifest import ManifestDTO
from datetime import datetime
from gdo_arch_utils.utils.file_utils import FileUtils as file_utils
from typing import List
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class ManifestUtils:
	task_manifest_list: List[ManifestDTO] = []

	@staticmethod
	def _replace_if_not_none(str_val):
		return "" if str_val is None else str_val.replace("'", "\\'").replace(",", "\\,")

	def mark_status_for_task(self):
		"""
					Will mark success in case of only success and warning log_types in the list.
					If there's any error will return error.
		"""
		from sys import exit
		if any(item for item in self.task_manifest_list if item.log_type.lower() == 'error'):
			logger.error("Found error, marking task as failed.")
			return exit(1)

	def append_to_manifest_list(
		self,
		log_type,
		log_message,
		sub_task,
		source = 'N/A',
		category = 'file',
		detailed_message = 'N/A',
		file_name = '',
		base_name_only = True
	):
		file_name_final = file_name
		if base_name_only:
			file_name_final = file_utils.get_basename(file_name)
		self.task_manifest_list.append(
			ManifestDTO(
				elt_ts = datetime.now(),
				log_type = log_type,
				category = category,
				log_message = ManifestUtils._replace_if_not_none(log_message),
				detailed_message = ManifestUtils._replace_if_not_none(detailed_message),
				file_name = file_name_final,
				sub_task = sub_task,
				source = source
			)
		)

	def get_manifest_list(self):
		return self.task_manifest_list

	def write_manifest(
		self,
		snowflake_utils_obj,
		try_number,
		dag_id,
		run_id,
		task_id,
		exec_date,
		sf_query_tag,
		sf_database,
		manifest_table_schema,
		manifest_table,
		insert_into_columns,
		application_name
	):
		insert_into_rows = []
		for manifest_entry in self.task_manifest_list:
			insert_into_rows.append(
				manifest_entry.get_as_str(
					try_number = try_number,
					dag_id = dag_id,
					run_id = run_id,
					task_id = task_id,
					exec_date = exec_date,
					elt_by = sf_query_tag,
					application = application_name
				)
			)

		snowflake_utils_obj.execute_insert_into(
			sf_table = manifest_table,
			sf_database = sf_database,
			sf_schema = manifest_table_schema,
			insert_into_columns = insert_into_columns,
			insert_into_rows = ','.join(insert_into_rows)
		)
