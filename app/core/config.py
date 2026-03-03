from sqlalchemy import Engine
from sqlmodel import  SQLModel, create_engine

class Database:
    def __init__(self) -> None:
        self.engine: Engine = create_engine(url="sqlite:///data/database.db")
        SQLModel.metadata.create_all(bind=self.engine)