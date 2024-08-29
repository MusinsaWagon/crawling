from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, Enum as SqlEnum
from config.mysql import Base
import logging
from enum import Enum

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
        high_price=int(product['sale_price']) if product['sale_price'] != 'N/A' else 0
        middle_price=int(product['sale_price']) if product['sale_price'] != 'N/A' else 0
        low_price=int(product['sale_price']) if product['sale_price'] != 'N/A' else 0
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
    