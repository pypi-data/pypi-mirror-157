import copy
import logging.config
import os
from datetime import datetime
from logging import Logger

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            'format': '[%(levelname)s][%(asctime)s][%(filename)s][line:%(lineno)d]:%(message)s',
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
        },
        "time": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "encoding": "utf8",
            "filename": f"app.log",
            "formatter": "default",
            "when": "midnight",
            "interval": 1,
            "backupCount": 10
        },
        # "file": {
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "level": "DEBUG",
        #     "encoding": "utf8",
        #     "filename": f"app2.log",
        #     "formatter": "default",
        #     "maxBytes": 10 * 1024 * 1024,
        #     "backupCount": 10
        # },
        # "mail": {
        #     "class": "logging.handlers.SMTPHandler",
        #     "level": "ERROR",
        #     "mailhost": ("smtp.qq.com"),
        #     "subject": '【自动化辅助工具】日志通知',
        #     "fromaddr": "84845615@qq.com",
        #     "toaddrs": "314666979@qq.com",
        #     "credentials": ("84845615@qq.com", "enyjdbtxxzqabjih"),
        #     "formatter": "default",
        # },
    },
    "loggers": {
        "console_logger": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "file_logger": {
            "handlers": ["time", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        # "mail_logger": {
        #     "handlers": ["mail", "console"],
        #     "level": "DEBUG",
        #     # 是否继续打印更高等级的日志
        #     "propagate": False,
        # }
    },
    "disable_existing_loggers": False,
}


def log(log_root_dir=".", level="DEBUG"):
    log_path = f"{os.path.abspath(log_root_dir)}"
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_config = copy.deepcopy(LOGGING_CONFIG)
    log_config["handlers"][log_root_dir] = log_config["handlers"]["time"]
    log_config["loggers"][log_root_dir] = log_config["loggers"]["file_logger"]
    del(log_config["handlers"]["time"])
    del (log_config["loggers"]["file_logger"])

    log_config["handlers"][log_root_dir]["filename"] = os.path.join(log_path, "app.log")
    log_config["loggers"][log_root_dir]["handlers"] = [log_root_dir, "console"]

    logging.config.dictConfig(log_config)
    my_log = logging.getLogger(log_root_dir)
    my_log.setLevel(level)
    return my_log


if __name__ == "__main__":
    log1 = log("./log1")
    import time
    while True:
        log1.debug(111)
        time.sleep(60)
