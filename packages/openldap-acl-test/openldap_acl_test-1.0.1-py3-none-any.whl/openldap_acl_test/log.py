from logging import WARNING, Filter, getLogger
from logging.config import dictConfig

from openldap_acl_test import __name__


class StdoutFilter(Filter):
    """自作Filterクラス

    WARNING以上のログを出力しないようにする。
    """

    def __init__(self, switch_level: int = WARNING):
        super().__init__()
        self.switch_level = switch_level

    def filter(self, record):
        return record.levelno < self.switch_level


def init_logger(loglevel: str = "INFO"):
    """
    loggerの初期設定と取得をする関数

    StdoutFilter を利用している。
    stdoutへ出力するハンドラにStdoutFilterを利用することで、
    INFO以下のログはstdoutへ出力し、WARNING以上のログはstderrへ出力するようになっている。
    """
    switch_level = WARNING
    logconfdict = {
        "version": 1,
        "formatters": {"console": {"format": "%(message)s"}},
        "filters": {
            "stdout": {
                "()": StdoutFilter,
                "switch_level": switch_level,
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "console",
                "stream": "ext://sys.stdout",
                "filters": ["stdout"],
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": switch_level,
                "formatter": "console",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            __name__: {
                "level": "DEBUG",
                "handlers": ["stdout", "stderr"],
                "propagate": False,
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["stdout", "stderr"],
        },
    }
    dictConfig(logconfdict)
    logger = getLogger(__name__)
    try:
        logger.setLevel(loglevel)
    except ValueError:
        logger.setLevel("INFO")
    return logger
