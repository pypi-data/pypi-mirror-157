import snowflake.connector
from dataclasses import dataclass
from gdo_arch_utils.utils.file_utils import FileUtils as file_utils
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils
from gdo_arch_utils.utils.traceback_utils import TracebackUtils as traceback_utils

logger = log_utils.get_logger()


class SnowflakeConnectionFailedError(Exception):
    def __init__(self, message):
        super().__init__(message)


@dataclass(frozen=True)
class SnowflakeConnection:
    """This class uses python context manager to open and close the connection automatically,
    based on scope of with keyword"""

    user: str
    password: str
    role: str
    account: str
    database: str
    warehouse: str
    schema: str
    query_tag: str
    con: object = None

    @classmethod
    def from_json(
        cls, sf_vault_path, role, database, schema, warehouse, account, query_tag
    ):
        sf_vault_json = file_utils.get_json_from_file(sf_vault_path)
        return cls(
            role=role,
            database=database,
            schema=schema,
            warehouse=warehouse,
            account=account,
            user=sf_vault_json["username"],
            password=sf_vault_json["password"],
            query_tag=query_tag,
        )

    def __enter__(self):
        try:
            object.__setattr__(
                self,
                "con",
                snowflake.connector.connect(
                    user=self.user,
                    password=self.password,
                    account=self.account,
                    role=self.role,
                    database=self.database,
                    schema=self.schema,
                    warehouse=self.warehouse,
                ),
            )
            logger.info("Connected to Snowflake")
            cursor = self.con.cursor()
            logger.info(f"Setting query tag value for session {self.query_tag}")
            cursor.execute(f"alter session set query_tag='{self.query_tag}'")
            return cursor
        except Exception as ex:
            traceback_utils.get_trace()
            raise SnowflakeConnectionFailedError(
                f"Could not get Snowflake cursor.{repr(ex)}"
            ) from ex

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.con:
            self.con.cursor().close()
            logger.debug("Closed Snowflake cursor")
            self.con.close()
            logger.info("Closed Snowflake connection")
