from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen = True)
class ManifestDTO:
	"""
	This class entries of utility table for logging manifest for each dag run.
	Triggering the utility mail dag with the required params will send a consolidated mail to the
	recipients with the logs for each steps/tries. Snowflake table {{ENV}}_DGTL_RAW.UTIL_COMMON.DAG_LOGS
	"""


	elt_ts: datetime
	log_type: str
	sub_task: str
	category: str
	log_message: str
	detailed_message: str
	file_name: str
	source: str

	def get_as_str(
		self, try_number, dag_id, run_id, task_id, exec_date, elt_by, application
	):

		return (
			f"({try_number},'{dag_id}','{run_id}','{task_id}','{exec_date}','{self.elt_ts}',"
			f"'{self.log_type}','{self.category}','{self.log_message}','{self.detailed_message}',"
			f"'{self.file_name}','{elt_by}','{self.sub_task}','{self.source}','{application}')"
		)
