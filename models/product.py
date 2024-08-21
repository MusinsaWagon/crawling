from sqlalchemy import Column, Integer, String, DateTime, BigInteger
import datetime
import logging
from config.mysql import Base
from config.mysql import Session
from models.category import get_or_create_category
from models.musinsa import create_musinsa
from models.product_history import create_musinsa_history

class Product(Base):
    __tablename__ = 'product'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    product_id = Column(Integer, unique=True, nullable=False)
    img_url = Column(String(200))
    name = Column(String(100))
    brand = Column(String(100))
    product_url = Column(String(200), unique=True)
    sale_price = Column(Integer)
    original_price = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
def create_product(product):
    try:
        product_name = product['name']
        brand = product['brand']
        product_id = int(product['product_id'])  
        category_id = get_or_create_category(product['category'], product['parent_category'])
        img_url=product['image_url'],
        product_url=product['product_url'],
        sale_price=int(product['sale_price']) if product['sale_price'] != 'N/A' else 0
        origin_price=int(product['original_price']) if product['original_price'] != 'N/A' else 0
        
        # Product 객체 생성
        new_product = Product(
            name=product_name,
            brand=brand,
            category_id=category_id,
            product_id=product_id,
            img_url=img_url,
            product_url=product_url,
            sale_price=sale_price,
            origin_price=origin_price
        )
        return new_product

    except KeyError as e:
        logging.error(f"product 생성 중 상 누락 발생: {e}")
        raise

    except Exception as e:
        logging.error(f"상품 생성 중 오류 발생: {e}")
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
                
                new_musinsa_history = create_musinsa_history(product, new_product.id)
                session.add(new_musinsa_history)
                
    except Exception as e:
        session.rollback()
        logging.error(f"초기 상품 저장 오류: {e}")
    finally:
        session.close()


