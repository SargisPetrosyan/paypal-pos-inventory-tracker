"""
Logging configuration module that sets up application-wide logging settings.
Configures log file location, format, and logging levels for the application.
"""

import logging


def setup_logger() -> None:
    logging.basicConfig(
        filename="logs/app_logs.log",
        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        filemode="w",
        force=True,
    )

    # Creating an object
    logger: logging.Logger = logging.getLogger()

    # Setting the threshold of logger to DEBUG
    logger.setLevel(level=logging.INFO)
