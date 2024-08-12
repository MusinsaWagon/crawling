import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from dotenv import load_dotenv
import datetime
from config.log import *

Base = declarative_base()
load_dotenv() # 환경변수 로딩

# MySQL 환경 변수 로딩
DB_NAME = os.getenv("DB_NAME")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")

# SQLAlchemy 설정
DATABASE_URI = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)

class Product(Base):
    __tablename__ = 'product'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    product_id = Column(Integer, unique=True, nullable=False)
    img_url = Column(String(200))
    name = Column(String(100))
    brand = Column(String(100))
    product_url = Column(String(200), unique=True)
    current_price = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    parent_category_id = Column(BigInteger, ForeignKey('category.id'), nullable=True)
    category_name = Column(String(50), nullable=False, unique=True)



# 테이블 생성
Base.metadata.create_all(engine)


def save_to_database(products_info):
    session = Session()
    try:
        with session.begin():
            for product in products_info:
                new_product = Product(
                    name=product['name'],
                    brand=product['brand'],
                    category_id=1, 
                    product_id=int(product['product_id']),
                    img_url=product['image_url'],
                    product_url=product['product_url'],
                    current_price=int(product['current_price']) if product['current_price'] != 'N/A' else 0
                )
                session.add(new_product)
    except Exception as e:
        session.rollback()
        logging.error(f"초기 상품 저장 오류: {e}")

def get_or_create_category(session, category_name):
    try:
        category = session.query(Category).filter_by(category_name=category_name).one()
    except NoResultFound:
        new_category = Category(category_name=category_name)
        session.add(new_category)
        session.commit()
        category = new_category
    
    return category.id