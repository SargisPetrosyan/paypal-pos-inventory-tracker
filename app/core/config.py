from typing import Any, Generator
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine, Session
from dataclasses import dataclass
import os


class DatabaseConnection:
    def __init__(self,database_url: str) -> None:
        self.engine: Engine = create_engine(url=database_url)
        SQLModel.metadata.create_all(bind=self.engine)

inventory_changes_database: DatabaseConnection = DatabaseConnection(database_url=os.environ["DB_URL"])
signing_key_database: DatabaseConnection = DatabaseConnection(database_url=os.environ["SIGNING_KEYS_DB_URL"])

def get_inventory_db_session() -> Generator[Session, Any, None]:
    with Session(inventory_changes_database.engine) as session:
        yield session

def get_signing_key_db_session() -> Generator[Session, Any, None]:
    with Session(signing_key_database.engine) as session:
        yield session
