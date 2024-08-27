from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Float, Enum as SqlEnum
import datetime
import logging
from config.mysql import Base
from config.mysql import Session
from models.category import get_or_create_category
from models.product_detail import create_product_detail
from models.product_history import create_product_history
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from enum import Enum

class ShopType(Enum):
    MUSINSA = "MUSINSA"
    ZIGZAG = "ZIGZAG"
    ABLY = "ABLY"
    BRANDY = "BRANDY"

class Product(Base):
    __tablename__ = 'product'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    product_num = Column(Integer, unique=True, nullable=False)
    img_url = Column(String(200))
    name = Column(String(100))
    brand = Column(String(100))
    origin_price = Column(Integer)
    star_score = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    shop_type = Column(SqlEnum(ShopType), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
def create_product(product):
    try:
        category_id = get_or_create_category(product['category'], product['parent_category'])
        product_num = int(product['product_num'])  
        img_url=product['image_url']
        product_name = product['name']
        brand = product['brand']
        origin_price=int(product['origin_price']) if product['origin_price'] != 'N/A' else 0
        star_score = float(product.get('star_score', 0.0))
        review_count = int(product.get('review_count', 0))
        like_count = int(product.get('like_count', 0))
        shop_type = ShopType.MUSINSA
        
        # Product 객체 생성
        new_product = Product(
            category_id=category_id,
            product_num=product_num,
            img_url=img_url,
            name=product_name,
            brand=brand,
            origin_price=origin_price,
            star_score=star_score,
            review_count=review_count,
            like_count=like_count,
            shop_type=shop_type
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
        for product in products_info:
            try:
                with session.begin(): 
                    new_product = create_product(product)
                    if new_product is None:
                        continue  # 생성 실패한 경우 다음으로 넘어감

                    session.add(new_product)
                    session.flush()  # ID를 얻기 위해 flush 수행
                    
                    new_product_detail = create_product_detail(product, new_product.id)
                    session.add(new_product_detail)

                    new_product_history = create_product_history(product, new_product.id)
                    session.add(new_product_history)

            except IntegrityError as ie:
                session.rollback()  # 트랜잭션을 롤백하여 무결성 문제 해결
                logging.error(f"중복 데이터로 인해 저장 실패: {product['product_num']}, 오류: {ie}")
                continue  # 다음 상품으로 넘어감

            except SQLAlchemyError as se:
                session.rollback()
                logging.error(f"SQLAlchemy 오류 발생: {se}")
                continue  # 다음 상품으로 넘어감

    except Exception as e:
        logging.error(f"초기 상품 저장 중 알 수 없는 오류 발생: {e}")

    finally:
        session.close()

