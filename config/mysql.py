import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, ForeignKey, Float
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


class Musinsa(Base):
    __tablename__ = 'musinsa'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey('product.id'), nullable=False)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)

Base.metadata.create_all(engine)

def create_product(product):
    try:
        product_name = product['name']
        brand = product['brand']
        product_id = int(product['product_id'])  
        category_id = get_or_create_category(product['category'], product['parent_category'])
        img_url=product['image_url'],
        product_url=product['product_url'],
        current_price=int(product['current_price']) if product['current_price'] != 'N/A' else 0
        
        # Product 객체 생성
        new_product = Product(
            name=product_name,
            brand=brand,
            category_id=category_id,
            product_id=product_id,
            img_url=img_url,
            product_url=product_url,
            current_price=current_price
        )
        return new_product

    except KeyError as e:
        logging.error(f"product 생성 중 상 누락 발생: {e}")
        raise

    except Exception as e:
        logging.error(f"상품 생성 중 오류 발생: {e}")
        return None
    
def create_musinsa(product, new_product_id):
    try:
        rating = float(product.get('star_count', 0.0))
        review_count = int(product.get('review_count', 0))
        like_count = int(product.get('like_count', 0))

        return Musinsa(
            product_id=new_product_id,  
            rating=rating,
            review_count=review_count,
            like_count=like_count
        )
    except (ValueError, TypeError) as e:
        logging.error(f"Musinsa 생성 중 데이터 변환 오류 발생: {e} - 데이터: {product}")
        return None
    
    except Exception as e:
        logging.error(f"Musinsa 생성 중 알 수 없는 오류 발생: {e}")
        return None
    
def save_product_info(products_info):
    session = Session()
    try:
        with session.begin():
            for product in products_info:
                # Product 생성
                new_product = create_product(product)
                session.add(new_product)
                session.flush()  # ID를 얻기 위해 flush 수행
                
                new_musinsa = create_musinsa(product, new_product.id)
                session.add(new_musinsa)
    except Exception as e:
        session.rollback()
        logging.error(f"초기 상품 저장 오류: {e}")
    finally:
        session.close()

def get_or_create_category(category_name, parent_category_name=None):
    session = Session()
    try:
        category = session.query(Category).filter_by(category_name=category_name).one()
    except NoResultFound:
        if parent_category_name:
            try:
                parent_category = session.query(Category).filter_by(category_name=parent_category_name).one()
            except NoResultFound:
                # 부모 카테고리도 없으면 생성
                parent_category = Category(category_name=parent_category_name)
                session.add(parent_category)
                session.commit()
        else:
            parent_category = None

        new_category = Category(category_name=category_name, parent_category_id=parent_category.id if parent_category else None)
        session.add(new_category)
        session.commit()
        category = new_category
    finally:
        session.close()
        
    return category.id
