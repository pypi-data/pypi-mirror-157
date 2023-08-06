from dataclasses import dataclass
from typing import List
from gdo_arch_utils.decorators.timed_decorator import timed
from gdo_arch_utils.connections.snowflake_connection import SnowflakeConnection
from gdo_arch_utils.utils.list_utils import ListUtils as list_utils
from tabulate import tabulate
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class SnowflakeExecutionError(Exception):
	"""Occurs when there error in copying file into Snowflake"""

	def __init__(self, message):
		self.message = message
		super().__init__(self, self.message)


class NoFilesFoundInSnowflakeStageError(Exception):
	"""Occurs when there's error in copying file into Snowflake"""

	def __init__(self, message):
		self.message = message
		super().__init__(self, self.message)


class ListFilesInStageLocationError(Exception):
	"""Occurs when there error in copying file into Snowflake"""

	def __init__(self, message):
		self.message = message
		super().__init__(self, self.message)


@dataclass
class SnowflakeUtils:
	"""Utility class for Snowflake"""
	sf_cursor: SnowflakeConnection

	def get_table_columns_as_list(self, cur, database, schema, table_name) -> List[str]:
		sql = f"SELECT * FROM {database}.{schema}.{table_name} LIMIT 0"
		logger.info(f"get_table_columns_as_list query {sql}")
		result_metadata_list = cur.describe(sql)
		return [
			col.name
			for col in result_metadata_list
		]

	def _get_list_of_files_in_stage_location(self, stage_location, stage_path):
		"""Returns list of file names in the provided stage location. Column 0 returns name"""
		try:
			return [
				col[0].replace(f"{stage_path}/", "")
				for col in self.sf_cursor.execute(f"list {stage_location}")
			]
		except Exception as ex:
			logger.error(repr(ex))
			raise ListFilesInStageLocationError(
				f"Unable to list files in : {stage_location}"
			) from ex

	def execute_copy_into(
		self,
		sf_table: str,
		sf_database: str,
		sf_schema: str,
		copy_into_columns: str,
		copy_from_columns: str,
		sf_stage_name: str,
		file_format: str,
		sf_ingestion_stage_path: str,
		stage_path: str,
		on_error: str = 'ABORT_STATEMENT',
		force: bool = False
	) -> None:
		staged_files = self._get_files_in_stage(
			sf_ingestion_stage_path = sf_ingestion_stage_path,
			stage_path = stage_path
		)

		logger.info(f"Staged files consolidated list is {staged_files}")

		if not staged_files:
			logger.error(f"No files to copy for stage {sf_ingestion_stage_path=} and "
			             f"{stage_path=}")
			raise NoFilesFoundInSnowflakeStageError("No files to perform copy into")

		for staged_file_chunk_list in list_utils.get_chunked_sub_lists(
				original_list = staged_files,
				chunk_size = 500
		):

			logger.info(f"Executing copy into for {staged_file_chunk_list}")
			sql = f"""
	            COPY INTO {sf_database}.{sf_schema}.{sf_table} ({copy_into_columns})
	            FROM (SELECT {copy_from_columns}
	            FROM @{sf_stage_name})
	            FILES=({list_utils.list_to_str_sep_delimiter(staged_file_chunk_list, ',')})
	            FILE_FORMAT=(TYPE={file_format},
	            NULL_IF = ('\\N', 'NULL', 'NUL', 'NA', 'na'))
	            ON_ERROR={on_error}
	            FORCE={force}
			"""

			self.execute_sql(sql)
			self._print_copy_into_details()

	def _get_column_names_from_last_query(self):
		return [column[0] for column in self.sf_cursor.description]

	def get_column_names_from_last_query(self):
		return self._get_column_names_from_last_query()

	def execute_insert_into(
		self,
		sf_table: str,
		sf_database: str,
		sf_schema: str,
		insert_into_columns: str,
		insert_into_rows: str
	) -> None:
		sql = f"""
	            INSERT INTO {sf_database}.{sf_schema}.{sf_table} ({insert_into_columns})
	            VALUES {insert_into_rows}
		"""
		self.execute_sql(sql)

	def _print_copy_into_details(self):
		logger.info("_print_copy_into_details")
		self._print_last_query_response()

	def print_last_query_response(self):
		self._print_last_query_response()

	def _print_last_query_response(self):
		headers = self._get_column_names_from_last_query()
		logger.info(tabulate(self.sf_cursor, headers = headers, tablefmt = 'pretty'))

	def get_scan_result_last_query(self):
		self.execute_sql("select * from table(result_scan(-1))")

	@timed
	def execute_sql(self, sql):
		try:
			self.sf_cursor.execute(sql)
			logger.info("Execution completed.")
		except Exception as ex:
			logger.error(repr(ex))
			raise SnowflakeExecutionError(
				f"Error in running Snowflake execute for sql : {sql}"
			) from ex
		finally:
			logger.info(f"sql => {sql}, query_id => {self.sf_cursor.sfqid}")

	def _get_files_in_stage(self, sf_ingestion_stage_path, stage_path):
		consolidated_stage_files = []
		for stage_location in sf_ingestion_stage_path.split(","):
			files_in_stage_location = self._get_list_of_files_in_stage_location(
				stage_location = stage_location, stage_path = stage_path
			)
			logger.info(
				f"Count {len(files_in_stage_location)}, Files for location {stage_location} are "
				f"{files_in_stage_location}"
			)
			consolidated_stage_files.extend(files_in_stage_location)
		logger.info(
			f"Count {len(consolidated_stage_files)}, Consolidated list {consolidated_stage_files}"
		)

		return list_utils.add_prefix_suffix_to_items_in_list(
			input_list = consolidated_stage_files,
			prefix = "'",
			suffix = "'"
		)
		
	def truncate_table(self, sf_table, sf_database, sf_schema):
		sql = f"""
				TRUNCATE TABLE IF EXISTS {sf_database}.{sf_schema}.{sf_table}
		"""
		self.execute_sql(sql)	
