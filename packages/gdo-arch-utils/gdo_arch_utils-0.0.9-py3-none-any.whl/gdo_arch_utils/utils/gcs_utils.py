from dataclasses import dataclass

from gdo_arch_utils.connections.gcs_client_connection import GcsClientConnection
from gdo_arch_utils.decorators.timed_decorator import timed
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class GcsUploadError(Exception):

	def __init__(self, message):
		self.message = message
		super().__init__(self, message)


class GcsDownloadError(Exception):

	def __init__(self, message):
		self.message = message
		super().__init__(self, message)

class GcsListError(Exception):

	def __init__(self, message):
		self.message = message
		super().__init__(self, message)

class GcsDeleteError(Exception):

	def __init__(self, message):
		self.message = message
		super().__init__(self, message)		


@dataclass
class GcsUtils:
	gcs_client: GcsClientConnection
	bucket_name: str

	@timed
	def upload_to_gcs(self, source_file_path, destination_file_path):
		try:
			bucket = self.gcs_client.get_bucket(self.bucket_name)
			blob = bucket.blob(destination_file_path)
			blob.upload_from_filename(source_file_path)
			logger.info(
				f"Uploaded {destination_file_path} successfully to GCP bucket {self.bucket_name}"
			)
		except Exception as ex:
			raise GcsUploadError(f"Exception in  copying to gcs {ex}")

	@timed
	def download_from_gcs(self, source_file_path, destination_file_path):
		try:
			bucket = self.gcs_client.get_bucket(self.bucket_name)
			blob = bucket.blob(source_file_path)
			blob.download_to_filename(destination_file_path)
			logger.info(f"Downloaded {source_file_path} successfully")
		except Exception as ex:
			raise GcsDownloadError(f"Exception in downloading from gcs {ex}")

	def check_if_file_exists(self, file_path) -> bool:
		bucket = self.gcs_client.get_bucket(self.bucket_name)
		blob = bucket.blob(file_path)
		logger.info(f"Checking if file {file_path} exists : {blob.exists()}")
		return blob.exists()

	def list_files(self,substring):
		try:
			bucket = self.gcs_client.get_bucket(self.bucket_name)
			files = bucket.list_blobs()
			fileList = [file.name for file in files if substring in file.name]
			return fileList	
		except Exception as ex:
			raise GcsListError(f"Exception in listing files {ex}")

	def delete_file(self, filename):
		try:
			bucket = self.gcs_client.get_bucket(self.bucket_name)
			bucket.delete_blob(filename)
			logger.info(f"{filename} deleted from bucket successfully.")
		except Exception as ex:
			raise GcsDeleteError(f"Exception in deleting {filename} file {ex}")
