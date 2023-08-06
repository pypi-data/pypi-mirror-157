from dataclasses import dataclass

from gdo_arch_utils.connections.sftp_connection import SftpConnection
from gdo_arch_utils.decorators.timed_decorator import timed
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils
from gdo_arch_utils.utils.file_utils import FileUtils as file_utils

logger = log_utils.get_logger()


class SftpFileNotFoundError(FileNotFoundError):
	"""Raised when file is not found with the given name at SFTP location"""

	def __init__(self, message):
		super().__init__(message)


@dataclass
class SftpUtils:
	sftp_con: SftpConnection

	@timed
	def download_from_sftp(self, sftp_file_path):
		if self.sftp_con:
			try:
				self.sftp_con.get(sftp_file_path, preserve_mtime = False)
				logger.info(f"Downloaded {sftp_file_path} from SFTP")
			except Exception as ex:
				logger.warning("Removing blank local file as file not found in SFTP location.")
				file_utils.delete_blank_file(file_utils.get_basename(sftp_file_path))
				raise SftpFileNotFoundError(
					f"File {sftp_file_path} not found at SFTP location"
				) from ex
