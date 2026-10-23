import hashlib
import hmac
import json

import pytest
from httpx import AsyncClient, Response
from pydantic import ValidationError

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import ZettleSigningKey
from app.tests.mocked_data import mock_invalid_inventory_data


@pytest.mark.anyio
async def test_webhook(async_client: AsyncClient) -> None:
    response: Response = await async_client.post(
        url="/inventory_tracker_webhook",
        json={
            "eventName": "TestMessage",
            "title": "New Book",
            "author": "Author 1",
            "description": "Description 1",
        },
    )

    assert response.status_code == 200
    assert response.json()["response"]["message"]


@pytest.mark.anyio
async def test_inventory_data_validation(
    async_client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    signing_key = "test-signing-key"
    async with session_factory() as session:
        session.add(ZettleSigningKey(signing_key=signing_key))
        await session.commit()

    body = json.dumps(mock_invalid_inventory_data, separators=(",", ":")).encode()
    signature = hmac.new(
        key=signing_key.encode(),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    with pytest.raises(ValidationError):
        await async_client.post(
            url="/inventory_tracker_webhook",
            content=body,
            headers={
                "content-type": "application/json",
                "x-izettle-signature": signature,
            },
        )
