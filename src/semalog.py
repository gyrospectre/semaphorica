import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging(log_level):
    logger = logging.getLogger()

    logger.setLevel(log_level)

    handler = logging.StreamHandler()

    handler.setFormatter(
        jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(levelname)s %(lambda)s %(message)s'
        )
    )

    logger.addHandler(handler)

    stdouthandler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stdouthandler)

    logger.removeHandler(logger.handlers[0])


def get_logger():
    logger = logging.getLogger()
    
    return logger