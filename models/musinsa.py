from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Float
from config.mysql import Base
import logging

class Musinsa(Base):
    __tablename__ = 'musinsa'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey('product.id'), nullable=False)
    star_score = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    
def create_musinsa(product, new_product_id):
    try:
        star_score = float(product.get('star_score', 0.0))
        review_count = int(product.get('review_count', 0))
        like_count = int(product.get('like_count', 0))

        return Musinsa(
            product_id=new_product_id,  
            star_score=star_score,
            review_count=review_count,
            like_count=like_count
        )
    except (ValueError, TypeError) as e:
        logging.error(f"Musinsa 생성 중 데이터 변환 오류 발생: {e} - 데이터: {product}")
        return None
    
    except Exception as e:
        logging.error(f"Musinsa 생성 중 알 수 없는 오류 발생: {e}")
        return None
    