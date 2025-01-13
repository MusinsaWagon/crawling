from sqlalchemy import Column, Integer, String, Date, BigInteger, Float, Enum as SqlEnum, ForeignKey
import datetime
import logging
from config.mysql import Base
from config.mysql import Session
from models.shop_type import ShopType
from models.category import get_or_create_category
from models.product_detail import create_product_detail, find_product_detail_by_id, update_product_detail_info
from models.product_history import create_product_history, count_product_history_by_product_id
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from enum import Enum

class Status(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    
class ProductRegistration(Base):
    __tablename__ = 'product_registration'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    shop_type = Column(SqlEnum(ShopType), nullable=False)
    url = Column(String(200), nullable=False, comment="등록 상품 URL")
    status = Column(SqlEnum(Status), nullable=False, default=Status.PENDING, comment="처리 상태")
    product_num = Column(Integer, unique=True, nullable=False)
    created_at = Column(Date, default=datetime.date.today)

def get_init_carwling_product_numbers(shop_type):
    session = Session()
    try:
        products = session.query(ProductRegistration).filter(
            ProductRegistration.shop_type == shop_type,
            ProductRegistration.status == Status.PENDING
        ).all()
        product_numbers = [product.product_num for product in products]
        return product_numbers
    except SQLAlchemyError as e:
        session.rollback()  
        logging.error(f"Product 번호 조회 중 오류 발생: {e}")
        return None
    finally:
        session.close()
        
def update_product_status(product_num, status):
    session = Session()
    try:
        product = session.query(ProductRegistration).filter(ProductRegistration.product_num == product_num).first()
        if product:
            product.status = status
            session.commit()
            # logging.info(f'상품 번호 {product_num}의 상태가 {status.name}로 변경되었습니다.')
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f'상품 상태 업데이트 중 오류 발생: {e}')
    finally:
        session.close()
        