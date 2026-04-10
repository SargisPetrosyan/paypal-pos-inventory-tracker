"""
Logging configuration module that sets up application-wide logging settings.
Configures log file location, format, and logging levels for the application.
"""

from datetime import datetime
from pytz import timezone
import logging

from app.constants import SWEDEN_TIMEZONE_NAME


def setup_logger() -> None:
    logging.basicConfig(
        filename="app/logs/app_logs.log",
        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        filemode="a",
        force=True,
    )
    logging.Formatter.converter = lambda *args: datetime.now(tz=timezone(SWEDEN_TIMEZONE_NAME)).timetuple()
    
    # Creating an object
    logger: logging.Logger = logging.getLogger()
    # Setting the threshold of logger to DEBUG
    logger.setLevel(level=logging.INFO)
