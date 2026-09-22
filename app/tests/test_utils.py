from email import message
from zoneinfo import ZoneInfo
from datetime import datetime,timezone

import pytest
from app.utils import CredentialContext, any_to_utc


def test_any_to_cet():

    timezone_1 = datetime(
        year=2026, month=9, day=22, hour=8, minute=0,
        tzinfo=ZoneInfo("Europe/London")
    )

    timezone_2 = datetime(
        year=2026, month=9, day=22, hour=9, minute=0,
        tzinfo=ZoneInfo("Europe/Stockholm")
    )

    utc_time = datetime(
    year=2026, month=9, day=22, hour=7, minute=0, second=0,
    tzinfo=timezone.utc
    )

    converted_tiemzone_1: datetime = any_to_utc(timezone_1)
    converted_tiemzone_2: datetime = any_to_utc(timezone_2)
    assert converted_tiemzone_1 == utc_time
    assert converted_tiemzone_2 == utc_time


@pytest.mark.parametrize(argnames="shop_name, mail, events", argvalues=[
    ("invalid_shop_name", "mail", ['event1','event2']),
])
def test_credentials_context(shop_name, events, mail):
    with pytest.raises(expected_exception=KeyError, match=f"{shop_name.upper()}_SUBSCRIPTION_UUID"):
        CredentialContext(
            shop_name=shop_name,
            mail=events,
            events=mail
        )
