import logging
import os

LOGGING_FORMAT = (
    "[%(asctime)s] %(name)s [%(levelname)7s] (%(filename)s:%(lineno)s) --- %(message)s"
)


def get_logger(name: str) -> "logging.Logger":
    """Make sure the logging format is sat before getting the logger.

    Args:
        name (str): The logger name.

    Returns:
        Logger: A logger instance with the given name.
    """
    logging.basicConfig(
        format=LOGGING_FORMAT, level=os.environ.get("LOG_LEVEL", "WARNING").upper()
    )

    return logging.getLogger(name)
