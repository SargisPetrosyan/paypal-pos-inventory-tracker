from sqlalchemy import Engine
from sqlmodel import  SQLModel, create_engine
import datetime

class Database:
    def __init__(self, time: datetime.datetime) -> None:
        self.engine: Engine = create_engine(url=f"sqlite:///database/database_{time.month}_{time.year}.db")
        SQLModel.metadata.create_all(bind=self.engine)