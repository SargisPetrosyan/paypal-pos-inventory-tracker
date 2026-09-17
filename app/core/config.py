from typing import Any, Generator
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine, Session
from dataclasses import dataclass


@dataclass
class DatabaseConnection:
    engine: Engine = create_engine(url='sqlite:///database/inventory_changes.db')

    def __post_init__(self):
        SQLModel.metadata.create_all(bind=self.engine)

database: DatabaseConnection = DatabaseConnection()

def get_session() -> Generator[Session, Any, None]:
    with Session(database.engine) as session:
        yield session
