from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from config.log import *
from config.models import Base

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    parent_category_id = Column(BigInteger, ForeignKey('category.id'), nullable=True)
    category_name = Column(String(50), nullable=False, unique=True)

