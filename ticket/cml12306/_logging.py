

import logging

__all__ = ('LogLevelFilter',)


class LogLevelFilter(logging.Filter):
    def __init__(self, log_level_no=logging.INFO):
        self._log_level_no = log_level_no

    def filter(self, record):
        if record.levelno == self._log_level_no:
            return 1
        else:
            return 0
