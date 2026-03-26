from datetime import datetime,timezone
from app.utils import RequestIdempotency, any_to_cet

def test_if_idempotency():
    idempotency = RequestIdempotency()
    request: dict[str, str]={
        "messageUuid" :"TestMessage",
        "title": "New Book", 
        "author": "Author 1", 
        "description": "Description 1"
        }
    idempotency.if_idempotent(request)
    result: bool = idempotency.if_idempotent(request)
    
    assert result==True

def test_any_to_cet():
    utc_time: datetime = datetime.strptime("2026-03-21 11:14:02+0000","%Y-%m-%d %H:%M:%S%z").astimezone(timezone.utc)
    convert_to_cet: datetime = any_to_cet(utc_time)

    cet: datetime =  datetime.strptime("2026-03-21 12:14:02+0001","%Y-%m-%d %H:%M:%S%z")

    assert convert_to_cet.hour==cet.hour
