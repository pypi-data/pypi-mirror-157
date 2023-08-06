from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class TracebackUtils:
    @staticmethod
    def get_trace():
        import traceback
        traceback.print_stack()