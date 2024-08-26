from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Enum as SqlEnum
from config.mysql import Base
import logging
from enum import Enum

class ShopType(Enum):
    MUSINSA = "MUSINSA"
    ZIGZAG = "ZIGZAG"
    ABLY = "ABLY"
    BRANDY = "BRANDY"


class ProductDetail(Base):
    __tablename__ = 'product_detail'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey('product.id'), nullable=False)
    purchase_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    shop_type = Column(SqlEnum(ShopType), nullable=False)
    
def create_product_detail(product, new_product_id):
    try:
        like_count = int(product.get('like_count', 0))
        purchase_count = 0 
        shop_type = ShopType.MUSINSA
        
        return ProductDetail(
            product_id=new_product_id,
            like_count=like_count,
            purchase_count=purchase_count,
            shop_type=shop_type
        )
         
    except (ValueError, TypeError) as e:
        logging.error(f"ProductDetail 생성 중 데이터 변환 오류 발생: {e} - 데이터: {product}")
        return None
    
    except Exception as e:
        logging.error(f"ProductDetail 생성 중 알 수 없는 오류 발생: {e}")
        return None
    