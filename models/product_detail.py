from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, Enum as SqlEnum
from config.mysql import Base
import logging
from enum import Enum
from config.mysql import Session
from sqlalchemy.exc import SQLAlchemyError

class ProductDetail(Base):
    __tablename__ = 'product_detail'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    high_price = Column(Integer, nullable=True)
    middle_price = Column(Integer, nullable=True)
    low_price = Column(Integer, nullable=True)
    product_url = Column(String(200), unique=True)
    
def create_product_detail(product):
    try:
        # 초기값은 판매가격으로 설정
        high_price=int(product['current_price']) if product['current_price'] != 'N/A' else 0
        middle_price=int(product['current_price']) if product['current_price'] != 'N/A' else 0
        low_price=int(product['current_price']) if product['current_price'] != 'N/A' else 0
        product_url=product['product_url']
        
        return ProductDetail(
            high_price=high_price,
            middle_price=middle_price,
            low_price=low_price,
            product_url=product_url
        )
         
    except (ValueError, TypeError) as e:
        logging.error(f"ProductDetail 생성 중 데이터 변환 오류 발생: {e} - 데이터: {product}")
        return None
    
    except Exception as e:
        logging.error(f"ProductDetail 생성 중 알 수 없는 오류 발생: {e}")
        return None

def find_product_detail_by_id(product_detail_id):
    session = Session()
    try:
        product_detail = session.query(ProductDetail).filter_by(id=product_detail_id).first()
        return product_detail
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"ProductDetail을 찾을 수 없습니다. {product_detail_id}: {e}")
        return None
    finally:
        session.close()
        
def update_product_detail_info(product_detail, current_price):
    if product_detail is None:
        return None
    
    if (product_detail.high_price < current_price):
        product_detail.high_price = current_price
        return product_detail
    elif (product_detail.low_price > current_price):
        product_detail.low_price = current_price
        return product_detail
    else:
        return None
