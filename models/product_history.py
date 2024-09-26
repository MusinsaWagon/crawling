from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Date
from config.mysql import Base
import datetime
import logging
from config.mysql import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

class ProductHistory(Base):
    __tablename__ = 'product_history'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(Date, default=datetime.date.today, nullable=False)
    
    
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
            logging.error(f"가격 데이터 히스토리 생성 중 Product를 찾지 못했습니다. 상품 번호 : {product.id}")
            return None
    except Exception as e:
        logging.error(f"Musinsa History 생성 중 오류 {product.id}: {e}")
        return None
    
    
def count_product_history_by_product_id(product_id):
    session = Session()
    try:
        # ProductHistory 테이블에서 해당 product_id의 히스토리 개수를 카운트
        history_count = session.query(func.count(ProductHistory.id)).filter_by(product_id=product_id).scalar()
        return history_count
    except SQLAlchemyError as e:
        logging.error(f"ProductHistory 개수를 카운트하는 중 오류가 발생했습니다.: {e}")
        return None
    finally:
        session.close()