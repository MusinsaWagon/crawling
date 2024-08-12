from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
import datetime
from config.log import *
from config.models import Base

class Product(Base):
    __tablename__ = 'product'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    product_id = Column(Integer, unique=True, nullable=False)
    img_url = Column(String(200))
    name = Column(String(100))
    brand = Column(String(100))
    product_url = Column(String(200), unique=True)
    current_price = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
