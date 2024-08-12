from sqlalchemy import Column, String, BigInteger, ForeignKey
from config.mysql import Base
from config.mysql import Session
from sqlalchemy.exc import NoResultFound

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    parent_category_id = Column(BigInteger, ForeignKey('category.id'), nullable=True)
    category_name = Column(String(50), nullable=False, unique=True)

def get_or_create_category(category_name, parent_category_name=None):
    session = Session()
    try:
        category = session.query(Category).filter_by(category_name=category_name).one()
    except NoResultFound:
        if parent_category_name:
            try:
                parent_category = session.query(Category).filter_by(category_name=parent_category_name).one()
            except NoResultFound:
                # 부모 카테고리도 없으면 생성
                parent_category = Category(category_name=parent_category_name)
                session.add(parent_category)
                session.commit()
        else:
            parent_category = None

        new_category = Category(category_name=category_name, parent_category_id=parent_category.id if parent_category else None)
        session.add(new_category)
        session.commit()
        category = new_category
    finally:
        session.close()
        
    return category.id

