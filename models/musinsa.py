from sqlalchemy import Column, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from config.models import Base

class Musinsa(Base):
    __tablename__ = 'musinsa'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey('product.id'), nullable=False)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)