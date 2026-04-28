"""
Logging configuration module that sets up application-wide logging settings.
Configures log file location, format, and logging levels for the application.
"""

from datetime import datetime
from logging.handlers import RotatingFileHandler
from pytz import timezone
import logging

from app.constants import SWEDEN_TIMEZONE_NAME


def setup_logger() -> None:
    filename="app/logs/drive_updater_logs.log"

    logging.basicConfig(
        filename=filename,
        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        filemode="a",
        force=True,
    )
    logging.Formatter.converter = lambda *args: datetime.now(tz=timezone(SWEDEN_TIMEZONE_NAME)).timetuple()

    my_handler = RotatingFileHandler(
        filename=filename, mode='a', 
        maxBytes=2*1024*1024, 
        backupCount=5, encoding=None,)
    
    # Creating an object
    logger: logging.Logger = logging.getLogger()

    logger.addHandler(my_handler)

    # Setting the threshold of logger to DEBUG
    logger.setLevel(level=logging.INFO)
