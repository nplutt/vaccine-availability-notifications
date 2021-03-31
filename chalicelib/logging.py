import logging
import os

from pythonjsonlogger import jsonlogger


def get_logger(name):
    logger = logging.getLogger(name)

    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)

    logger.addHandler(logHandler)
    logger.setLevel(os.environ["LOG_LEVEL"])
    logger.propagate = False

    return logger
