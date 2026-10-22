from typing import Any, Generator
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel, create_engine, Session
from dataclasses import dataclass
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from typing import AsyncGenerator


class DatabaseConnection:
    def __init__(self,database_url: str) -> None:
        self.async_engine: AsyncEngine = create_async_engine(
            url=database_url,
            echo=True,
            future=True,)

    async def create_tables(self) -> None:
        async with self.async_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

inventory_changes_database: DatabaseConnection = DatabaseConnection(database_url=os.environ["DB_URL"])
signing_key_database: DatabaseConnection = DatabaseConnection(database_url=os.environ["SIGNING_KEYS_DB_URL"])

async def get_inventory_db_session():
     async with AsyncSession(inventory_changes_database.async_engine) as session:
        yield session

async def get_signing_key_db_session():
    async with AsyncSession(signing_key_database.async_engine) as session:
        yield session
