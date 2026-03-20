from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading.db")

connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def create_db_and_tables():
    from .models import symbol, signal, execution, validation, alert, system, broker
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
