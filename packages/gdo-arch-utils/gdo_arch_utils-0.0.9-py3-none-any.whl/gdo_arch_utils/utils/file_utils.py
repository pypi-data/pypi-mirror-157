from os import (
	listdir,
	path,
	makedirs,
	remove,
)
from os.path import getsize
import json
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class FileUtils:

	@staticmethod
	def files_in_dir_list(dir_to_list_files):
		"""Return list of all files in a directory"""
		return [
			file
			for file in listdir(dir_to_list_files)
			if path.isfile(file)
		]

	@staticmethod
	def get_size(file_path) -> str:
		if FileUtils.check_file_exists(file_path):
			return f"File size for {file_path} is " \
			       f"{round(getsize(file_path) / (1024 * 1024), 2)} MB"
		else:
			return f"File not found at {file_path}"

	@staticmethod
	def get_json_from_file(file_path):
		try:
			with open(file_path, encoding = 'utf-8') as sftp_json_file:
				return json.load(sftp_json_file)
		except FileNotFoundError as ex:
			raise FileNotFoundError(f"Error in getting json file {file_path}") from ex

	@staticmethod
	def print_files_in_dir(dir_to_list_files):
		"""Print all files in a directory"""
		for item in FileUtils.files_in_dir_list(dir_to_list_files):
			logger.info(item)

	@staticmethod
	def check_file_exists(file_name):
		from pathlib import Path
		path = Path(file_name)
		if path.is_file():
			logger.info(f'File {file_name} exists')
			return True
		return False

	@staticmethod
	def check_dir_exists_else_create(file_path):
		"""Creates dir if not exists"""
		dir_path = FileUtils._get_dir_path(file_path)
		makedirs(dir_path, exist_ok = True)
		logger.info(f"Directory created {dir_path} if not exists")

	@staticmethod
	def _get_dir_path(file_path):
		dir_name = path.dirname(file_path)
		logger.info(f"Getting dir path for {file_path} => {dir_name}")
		return dir_name

	@staticmethod
	def delete_blank_file(file_path):
		if FileUtils.get_file_size(file_path) == 0:
			FileUtils.delete_file(file_path)
		else:
			logger.info(f"File {file_path} is not blank")

	@staticmethod
	def delete_file(file_path):
		if path.isfile(file_path):
			remove(file_path)
			logger.info(f"File {file_path} has been deleted")
		else:
			logger.info(f"File {file_path} does not exist")

	@staticmethod
	def print_size(file_path):
		if path.isfile(file_path):
			import os
			logger.info(
				f"File size of file {file_path} is "
				f"{round(os.path.getsize(file_path) / (1024 * 1024), 2)} MB"
			)

	@staticmethod
	def get_file_size(file_path):
		if path.isfile(file_path):
			import os
			return os.path.getsize(file_path)

	@staticmethod
	def get_basename(file_path):
		"""If file_path is /a/b/c.txt returns c.txt"""
		import os
		basename = os.path.basename(file_path)
		return basename

	@staticmethod
	def get_file_name_stem(file_path):
		"""If file_path is /a/b/c.txt returns c"""
		basename = FileUtils.get_basename(file_path)
		return basename.split(".")[0]
