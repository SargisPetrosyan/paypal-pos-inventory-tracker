from sqlalchemy import Engine
from sqlmodel import  SQLModel, create_engine
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self) -> None:
        self.engine: Engine = create_engine(url="sqlite:///database/database.db")
        SQLModel.metadata.create_all(bind=self.engine)