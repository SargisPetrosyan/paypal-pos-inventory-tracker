import hashlib
import hmac
import json

import pytest
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import ZettleSigningKey
from app.tests.mocked_data import mock_valid_inventory_data


@pytest.mark.anyio
async def test_create_inventory_record(
    async_client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    signing_key = "test-signing-key"
    async with session_factory() as session:
        session.add(ZettleSigningKey(signing_key=signing_key))
        await session.commit()

    body = json.dumps(mock_valid_inventory_data, separators=(",", ":")).encode()
    signature = hmac.new(
        key=signing_key.encode(),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    response: Response = await async_client.post(
        url="/inventory_tracker_webhook",
        content=body,
        headers={
            "content-type": "application/json",
            "x-izettle-signature": signature,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Data registered in db"}


@pytest.mark.anyio
async def test_duplicate_inventory_record(
    async_client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    signing_key = "test-signing-key"
    async with session_factory() as session:
        session.add(ZettleSigningKey(signing_key=signing_key))
        await session.commit()

    body = json.dumps(mock_valid_inventory_data, separators=(",", ":")).encode()
    signature = hmac.new(
        key=signing_key.encode(),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    headers = {
        "content-type": "application/json",
        "x-izettle-signature": signature,
    }
    await async_client.post(
        url="/inventory_tracker_webhook",
        content=body,
        headers=headers,
    )
    response_2: Response = await async_client.post(
        url="/inventory_tracker_webhook",
        content=body,
        headers=headers,
    )

    assert response_2.status_code == 200
    assert response_2.json()[0] == {"message": "Data already exist in db"}
