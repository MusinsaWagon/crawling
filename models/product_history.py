from sqlalchemy import Column, Integer, BigInteger, ForeignKey, DateTime
from config.mysql import Base
import datetime

class ProductHistory(Base):
    __tablename__ = 'product_history'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    
