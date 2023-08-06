import base64
import json
from dataclasses import (
	dataclass,
	field,
)
from google.cloud import storage
from typing import List
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils
from gdo_arch_utils.utils.traceback_utils import TracebackUtils as traceback_utils

logger = log_utils.get_logger()


class GoogleStorageClientError(FileNotFoundError):
	def __init__(self, message):
		super().__init__(message)


class GcsConnectionFailedError(Exception):
	def __init__(self, message):
		super().__init__(message)


class GcsJsonConfigFileNotFoundError(FileNotFoundError):
	def __init__(self, message):
		self.message = message
		super().__init__(self, message)


@dataclass(frozen = True)
class GcsClientConnection:
	"""This class uses python context manager to open and close the connection automatically,
	based on scope of with keyword"""

	gcs_vault_path: str
	is_vault_base64_encoded: bool = True
	gcs_client: object = None
	scopes: List = field(default_factory = lambda: [""])

	def _get_storage_client(self):
		try:
			gcs_sa = self._get_gcs_vault_json()
			with open("gcs_sa.json", "w", encoding = "utf-8") as sa_json:
				json.dump(gcs_sa, sa_json)
			return storage.Client.from_service_account_json("gcs_sa.json")
		except FileNotFoundError as fnf:
			raise GoogleStorageClientError(
				f"Exception in reading gcs vault file {fnf}"
			) from fnf

	def _get_json_from_file(self):
		try:
			with open(self.gcs_vault_path) as json_file:
				return json.load(json_file)
		except FileNotFoundError as fnf:
			raise GcsJsonConfigFileNotFoundError(
				f"Exception in reading JSON config file"
			) from fnf

	def _get_gcs_vault_json(self):
		if self.is_vault_base64_encoded:
			gcs_json_mapping = self._get_json_from_file()["key"]
			base64_bytes = gcs_json_mapping.encode("ascii")
			sample_string_bytes = base64.b64decode(base64_bytes)
			sample_string = sample_string_bytes.decode("ascii")
			return json.loads(sample_string)
		return self._get_json_from_file()

	def __enter__(self):
		try:
			object.__setattr__(self, "gcs_client", self._get_storage_client())
			logger.info("GCS connection established successfully")
			return self.gcs_client
		except Exception as ex:
			traceback_utils.get_trace()
			raise GcsConnectionFailedError(
				f"Could not get gcs connection.{repr(ex)}"
			) from ex

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.gcs_client:
			logger.info("Closing GCS connection")
			self.gcs_client.close()
		else:
			logger.warning("GCS connection not found")
