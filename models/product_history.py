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
    

def create_product_history_by_price(price, product_num, shop_type):
    from models.product import Product  # import를 함수 내에서 실행하여 순환 참조를 피함
      
    session = Session()
    try:
        product = session.query(Product).filter_by(product_num=product_num, shop_type=shop_type).first()

        if product : 
            product_history = ProductHistory(
                product_id=product.id,
                price=price,
                created_at=datetime.datetime.utcnow().date() 
            )
            
            # 데이터베이스에 기록 (선택 사항)
            session.add(product_history)
            session.commit()
            
            return product_history
        else:
            logging.error(f"가격 데이터 히스토리 생성 중 Product를 찾지 못했습니다. 상품 번호 : {product_num}")
            return None
        
    except SQLAlchemyError as e:
        session.rollback()  
        logging.error(f"Musinsa History 생성 중 오류 {product_num}: {e}")
        return None

    finally:
        session.close() 

  