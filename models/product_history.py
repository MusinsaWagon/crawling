from sqlalchemy import Column, Integer, BigInteger, ForeignKey, DateTime
from config.mysql import Base
import datetime
import logging

class ProductHistory(Base):
    __tablename__ = 'product_history'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow().date(), nullable=False)
    
    
def create_product_history(product, new_product_id):
    try:
        sale_price=int(product['sale_price']) if product['sale_price'] != 'N/A' else 0

        product_history = ProductHistory(
            product_id=new_product_id,
            price=sale_price,
            created_at=datetime.datetime.utcnow().date() 
        )

        return product_history

    except Exception as e:
        logging.error(f"Musinsa History 생성 중 오류 {new_product_id}: {e}")
        return None