from datetime import datetime,timezone
from app.utils import any_to_cet


def test_any_to_cet():
    utc_time: datetime = datetime.strptime("2026-03-21 11:14:02+0000","%Y-%m-%d %H:%M:%S%z").astimezone(timezone.utc)
    convert_to_cet: datetime = any_to_cet(utc_time)

    cet: datetime =  datetime.strptime("2026-03-21 12:14:02+0001","%Y-%m-%d %H:%M:%S%z")

    assert convert_to_cet.hour==cet.hour
