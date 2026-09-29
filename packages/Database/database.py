from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import psycopg2
import os

URL_DATABASE = 'postgresql+psycopg2://postgres:Root@localhost:5432/demo_db'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)