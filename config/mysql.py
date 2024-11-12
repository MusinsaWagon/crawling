import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from config.log import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
load_dotenv() # 환경변수 로딩

# MySQL 환경 변수 로딩
DB_NAME = os.getenv("LOCAL_DB_NAME")
MYSQL_HOST = os.getenv("LOCAL_MYSQL_HOST")
MYSQL_PASSWORD = os.getenv("LOCAL_MYSQL_PASSWORD")
MYSQL_PORT = os.getenv("LOCAL_MYSQL_PORT")
MYSQL_USERNAME = os.getenv("LOCAL_MYSQL_USERNAME")

# SQLAlchemy 설정
DATABASE_URI = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

