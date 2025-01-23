from sqlalchemy import Column, String, BigInteger, ForeignKey
from config.mysql import Base
from config.mysql import Session
import logging

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    parent_category_id = Column(BigInteger, ForeignKey('category.id'), nullable=True)
    category_name = Column(String(50), nullable=False, unique=True)

def get_or_create_category(category_name, parent_category_name):
    session = Session()
    try:
        # 기존 카테고리를 조회
        category = session.query(Category).filter_by(category_name=category_name).one_or_none()
        if category is None:
            # 부모 카테고리 조회 또는 생성
            if parent_category_name:
                parent_category = session.query(Category).filter_by(category_name=parent_category_name).one_or_none()
                if parent_category is None:
                    parent_category = Category(category_name=parent_category_name)
                    session.add(parent_category)
                    session.flush()
            else:
                parent_category = None

            category = Category(category_name=category_name, parent_category_id=parent_category.id if parent_category else None)
            session.add(category)
            session.commit()
        
        # 세션에 바인딩된 객체를 반환
        return category.id

    except Exception as e:
        logging.error(f"카테고리 생성 중 오류 발생: {e}")
        session.rollback()
        return None

    finally:
        session.close()

