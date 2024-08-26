from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Float
import datetime
import logging
from config.mysql import Base
from config.mysql import Session
from models.category import get_or_create_category
from models.product_detail import create_product_detail
from models.product_history import create_product_history

class Product(Base):
    __tablename__ = 'product'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    product_num = Column(Integer, unique=True, nullable=False)
    img_url = Column(String(200))
    name = Column(String(100))
    brand = Column(String(100))
    product_url = Column(String(200), unique=True)
    sale_price = Column(Integer)
    origin_price = Column(Integer)
    star_score = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
def create_product(product):
    try:
        product_name = product['name']
        brand = product['brand']
        product_num = int(product['product_num'])  
        category_id = get_or_create_category(product['category'], product['parent_category'])
        img_url=product['image_url']
        product_url=product['product_url']
        sale_price=int(product['sale_price']) if product['sale_price'] != 'N/A' else 0
        origin_price=int(product['origin_price']) if product['origin_price'] != 'N/A' else 0
        star_score = float(product.get('star_score', 0.0))
        review_count = int(product.get('review_count', 0))
        
        # Product 객체 생성
        new_product = Product(
            name=product_name,
            brand=brand,
            category_id=category_id,
            product_num=product_num,
            img_url=img_url,
            product_url=product_url,
            sale_price=sale_price,
            origin_price=origin_price,
            star_score=star_score,
            review_count=review_count
        )
        return new_product

    except KeyError as e:
        logging.error(f"product 생성 중 상 누락 발생: {e}")
        raise

    except Exception as e:
        logging.error(f"product 생성 중 오류 발생: {e}")
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
                
                new_musinsa = create_product_detail(product, new_product.id)
                session.add(new_musinsa)
                
                new_musinsa_history = create_product_history(product, new_product.id)
                session.add(new_musinsa_history)
                
    except Exception as e:
        session.rollback()
        logging.error(f"초기 상품 저장 오류: {e}")
    finally:
        session.close()


