import time

from functools import wraps
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


def timed(func):
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as ex:
            logger.error(ex)
            raise ex
        finally:
            end_time = time.time()
            time_delta = end_time - start_time
            time_delta_minutes = round(time_delta / 60, 2)
            time_delta_seconds = round(time_delta)
            logger.info(
                f"{func.__name__} completed processing in {time_delta_seconds} s or {time_delta_minutes} mins"
            )

    return wrapper
