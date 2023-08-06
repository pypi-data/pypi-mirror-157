import pandas as pd
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class PandasUtils:
	"""Pandas utility class"""

	@staticmethod
	def change_to_parquet_and_compress(
		dataframe_to_process,
		parquet_file_path,
		column_mapping,
		compression_type = None
	):
		df = dataframe_to_process.convert_dtypes()

		df.rename(
			columns = column_mapping,
			inplace = True
		)

		df.to_parquet(
			path = parquet_file_path,
			compression = compression_type,
			index = False
		)

	@staticmethod
	def _replace_column(replace_column_str_mapping, df):
		"""Replace columns like replace col 1 with col_1 by passing a json mapping"""
		for replace_str, replace_with_str in replace_column_str_mapping.items():
			logger.debug(f"Replacing {replace_str} with {replace_with_str} inside _replace_column")
			df.columns = df.columns.str.replace(replace_str, replace_with_str)

	@staticmethod
	def add_col_with_static_val(df, col_with_static_val_mapping = None):
		if col_with_static_val_mapping:
			for col_name, value in col_with_static_val_mapping.items():
				logger.debug(f"Adding static column {col_name} with value {value}")
				df[col_name] = value

	@staticmethod
	def _change_columns_case(df, column_case = None):
		"""
			Supported cases are lower and upper for now, \
			can be extended to support
			other cases like camel case
		"""
		if column_case == 'upper':
			df.columns = df.columns.str.upper()
		elif column_case == 'lower':
			df.columns = df.columns.str.lower()

	@staticmethod
	def write_chunks_to_parquet_and_compress(
		dataframe_chunks,
		parquet_file_path,
		parquet_file_path_placeholder,
		replace_column_str_mapping = None,
		col_with_static_val_mapping = None,
		column_mapping = None,
		compression_type = None,
		column_case = None
	):
		file_counter = 0
		logger.info(f"{parquet_file_path=},{parquet_file_path_placeholder=}")
		for count, dataframe_to_process in enumerate(dataframe_chunks):
			path = parquet_file_path.replace(parquet_file_path_placeholder, str(count))
			logger.debug(f"Writing to file {path}")
			df = dataframe_to_process.convert_dtypes()
			if replace_column_str_mapping:
				PandasUtils._replace_column(replace_column_str_mapping, df)
			if column_mapping:
				df.rename(
					columns = column_mapping,
					inplace = True
				)
			PandasUtils._change_columns_case(df, column_case)
			if col_with_static_val_mapping:
				PandasUtils.add_col_with_static_val(df, col_with_static_val_mapping)

			df.to_parquet(
				path = path,
				compression = compression_type,
				index = False
			)
			file_counter += 1
		return file_counter

	@staticmethod
	def read_csv_into_dataframe(csv_file_path, encoding = None, dtype = 'str', separator = ','):
		return pd.read_csv(
			filepath_or_buffer = csv_file_path,
			encoding = encoding,
			dtype = dtype,
			sep = separator,
		)

	@staticmethod
	def _get_column_name_list(file_path, encoding, separator, replace_column_names_mapping):
		"""Assuming first row of csv contains header"""
		with open(file_path, encoding = encoding) as file:
			column_names_row = file.readline()
			if replace_column_names_mapping:
				for replace_str, replace_with_str in replace_column_names_mapping.items():
					logger.debug(f"Replacing {replace_str} with {replace_with_str}")
					column_names_row = column_names_row.replace(replace_str, replace_with_str)

			columns = list(column_names_row.split(separator))
			logger.debug(f"Columns in file {columns} inside get_column_name_list")
			return columns

	@staticmethod
	def return_csv_chunks(
		csv_file_path, encoding = None,
		dtype = 'str',
		separator = ',',
		chunksize = 1000000,
		replace_column_names_mapping = None,
		has_header = True,
		skip_rows = 0,
		doublequote = False,
		quotechar = '"',
		na_filter = False
	):
		"""Pass has_header=False if file does not have a header or want to skip detecting columns
		from the row."""
		usecols = None
		if has_header:
			usecols = PandasUtils._get_column_name_list(
				csv_file_path, encoding, separator, replace_column_names_mapping
			)

		return pd.read_csv(
			filepath_or_buffer = csv_file_path,
			encoding = encoding,
			dtype = dtype,
			sep = separator,
			skiprows = skip_rows,
			usecols = usecols,
			doublequote = doublequote,
			quotechar = quotechar,
			na_filter = na_filter,
			chunksize = chunksize
		)
