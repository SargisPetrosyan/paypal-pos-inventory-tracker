from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


class DatabaseConnection:
    def __init__(self,database_url: str) -> None:
        self.async_engine: AsyncEngine = create_async_engine(
            url=database_url,
            echo=True,
            future=True,)

    async def create_tables(self) -> None:
        async with self.async_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

db: DatabaseConnection = DatabaseConnection(database_url=os.environ["DB_URL"])

async def create_database_tables() -> None:
    await db.create_tables()

async def get_db_session():
    async with AsyncSession(db.async_engine) as session:
        yield session
