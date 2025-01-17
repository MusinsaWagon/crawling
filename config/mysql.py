import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from config.log import *
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path

Base = declarative_base()

# 공용 환경변수 로드
load_dotenv(".env")

# 환경에 따라 다른 .env 파일 로드
environment = os.getenv("ENV")  # 배포 환경마다 다르게 설저
if environment == "prod":
    load_dotenv(".env.prod", override=True)
    print("프로덕")
else:
    load_dotenv(".env.dev", override=True)
    print("로컬")
    
# MySQL 환경 변수 로딩
DB_NAME = os.getenv("DB_NAME")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
try:
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
except ValueError:
    raise ValueError("MYSQL_PORT 환경변수 값이 잘못되었습니다. 정수 포트를 설정하세요.")
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")

# SQLAlchemy 설정
DATABASE_URI = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

