import pysftp
from dataclasses import dataclass
from gdo_arch_utils.utils.file_utils import FileUtils as file_utils
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils
from gdo_arch_utils.utils.traceback_utils import TracebackUtils as traceback_utils
logger = log_utils.get_logger()


class SftpConnectionFailedError(Exception):
    def __init__(self, message):
        super().__init__(message)


class SftpCnoptsError(FileNotFoundError):
    def __init__(self, message):
        super().__init__(message)


class SftpWriteToFileError(Exception):
    def __init__(self, message):
        super().__init__(message)


@dataclass(frozen=True)
class SftpConnection:
    """This class uses python context manager to open and close the connection automatically,
    based on scope of with keyword"""

    hostname: str
    port: int
    username: str
    password: str
    cnopts: str
    sftp_conn: object = None

    def __post_init__(self):
        object.__setattr__(self, "cnopts", self._get_cnopts(self.cnopts))

    @classmethod
    def from_json(cls, sftp_vault_path):
        sftp_json_str = file_utils.get_json_from_file(sftp_vault_path)
        return cls(
            port=int(sftp_json_str["Port"]),
            hostname=sftp_json_str["Hostname"],
            username=sftp_json_str["Username"],
            password=sftp_json_str["Password"],
            cnopts=sftp_json_str["Cnopts"],
        )

    def _get_cnopts(self, cnopts_str):
        try:
            self._write_to_file("cnopts.key", cnopts_str)
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys.load("cnopts.key")
            return cnopts
        except FileNotFoundError as ex:
            raise SftpCnoptsError("Exception in getting cnopts") from ex

    @staticmethod
    def _write_to_file(file_name, str_to_write):
        try:
            with open(file_name, "w") as file_output:
                file_output.write(str_to_write)
        except Exception as ex:
            raise SftpWriteToFileError("Could not write to file") from ex

    def __enter__(self):
        try:
            object.__setattr__(
                self,
                "sftp_conn",
                pysftp.Connection(
                    host=self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    cnopts=self.cnopts,
                ),
            )
            logger.info("SFTP connection established successfully")
            return self.sftp_conn
        except Exception as ex:
            traceback_utils.get_trace()
            raise SftpConnectionFailedError(
                f"Could not get sftp connection.{repr(ex)}"
            ) from ex

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sftp_conn:
            logger.info("Closing SFTP connection")
            self.sftp_conn.close()
        else:
            logger.warning("SFTP connection not found")
