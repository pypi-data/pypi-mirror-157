#### extracts the SAPMC credentials from the json stored in the vault path
import json
import os

from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()

class CredentialNotFound(Exception):
	def __init__(self, message):
		super().__init__(message)

class SapMCConnection:
	"""This class extracts the credentials json from the vault path"""

	sapmc_vault_path: str

	def __init__(self):
		logger.info("Generating SAPMC Connection class")

	def get_sapmc_api_creds(self,sapmc_vault_path):
		try:
			if not os.path.exists(sapmc_vault_path):
				raise CredentialNotFound(f"No credential file found in path {sapmc_vault_path}")
			with open(sapmc_vault_path) as fp:
				dict_ = json.load(fp)
			return dict_
		except json.JSONDecodeError:
			raise CredentialNotFound("Invalid json format for credentials")
		except Exception as e:
			raise e