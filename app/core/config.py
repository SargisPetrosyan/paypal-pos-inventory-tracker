from sqlalchemy import Engine
from sqlmodel import  SQLModel, create_engine
import datetime

class Database:
    def __init__(self, time: datetime.datetime) -> None:
        self.engine: Engine = create_engine(url=f"sqlite:///database/database.db_{time.month}_{time.year}")
        SQLModel.metadata.create_all(bind=self.engine)