import logging
import os

LOGGING_FORMAT = (
    "[%(asctime)s] %(name)s [%(levelname)7s] (%(filename)s:%(lineno)s) --- %(message)s"
)

logging.basicConfig(
    format=LOGGING_FORMAT, level=os.environ.get("LOG_LEVEL", "WARNING").upper()
)


def get_logger(name: str):
    return logging.getLogger(name)
