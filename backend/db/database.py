import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from dotenv import load_dotenv
class Base(DeclarativeBase):
    pass


from pathlib import Path
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_TEST_URL = os.getenv('DATABASE_URL').strip()
engine = create_engine(DATABASE_TEST_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
def get_session():
    with SessionLocal() as session:
        yield session