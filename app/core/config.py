from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine, Session
from dataclasses import dataclass


@dataclass
class DatabaseConnection:
    engine: Engine = create_engine(url=f"sqlite:///database/inventory_changes.db")

    def __post_init__(self):
        SQLModel.metadata.create_all(bind=self.engine)


def get_session(engine: Engine):
    with Session(engine) as session:
        yield session
