from sqlalchemy import Engine
from sqlmodel import  SQLModel, create_engine,Session
import datetime


class DatabaseConnection:
    def __init__(self) -> None:
        self.engine: Engine = create_engine(url=f"sqlite:///database/inventory_changes.db")
        SQLModel.metadata.create_all(bind=self.engine)

def get_session(engine:Engine):
    with Session(engine) as session:
        yield session