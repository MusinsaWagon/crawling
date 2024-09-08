from sqlalchemy import Column, Integer, BigInteger, ForeignKey, DateTime
from config.mysql import Base
import datetime
import logging
from config.mysql import Session
from sqlalchemy.exc import SQLAlchemyError

class ProductHistory(Base):
    __tablename__ = 'product_history'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow().date(), nullable=False)
    
    
def create_product_history(price, product):
    try:
        if product : 
            product_history = ProductHistory(
                product_id=product.id,
                price=price,
                created_at=datetime.datetime.utcnow().date() 
            )

            return product_history
        else:
            logging.error(f"가격 데이터 히스토리 생성 중 Product를 찾지 못했습니다. 상품 번호 : {product_num}")
            return None

    except Exception as e:
        logging.error(f"Musinsa History 생성 중 오류 {product.id}: {e}")
        return None
    