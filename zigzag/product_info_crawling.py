import sys
import os
import requests
import json
import time
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
from dotenv import load_dotenv
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.log import *
from config.mysql import *
from models.product import save_product_info
from config.file import read_product_numbers
from models.shop_type import ShopType

# 지그재그 상품 기본 URL
USER_AGENT = os.getenv("USER_AGENT")
ZIGZAG_PRODUCT_URL = os.getenv("ZIGZAG_PRODUCT_URL")
ZIGZAG_PRODUCTS_FILE_PATH = os.getenv("ZIGZAG_PRODUCTS_FILE_PATH")

load_dotenv() # 환경변수 로딩

# 리뷰 수 & 평점
def get_review_summary(catalog_product_id, headers, limit_count=5, order="BEST_SCORE_DESC"):

    # catalog_product_id (str): 상품 ID
    # limit_count (int): 가져올 리뷰 제한 수 (기본값: 5)
    # order (str): 리뷰 정렬 기준 (기본값: "BEST_SCORE_DESC")

    url = "https://api.zigzag.kr/api/2/graphql/GetPdpIntegratedData"

    payload = {
        "operationName": "GetPdpIntegratedData",
        "variables": {
            "catalog_product_id": catalog_product_id,
            "limit_count": limit_count,
            "order": order
        },
        "query": """
        query GetPdpIntegratedData(
            $catalog_product_id: ID!, 
            $limit_count: Int, 
            $order: ProductReviewListOrderType
        ) {
            related_product_review_summary(product_id: $catalog_product_id) {
                all_count
                ratings_average
            }
            product_review_list(
                product_id: $catalog_product_id, 
                limit_count: $limit_count, 
                order: $order
            ) {
                item_list {
                    id
                    contents
                    rating
                    reviewer {
                        profile {
                            masked_email
                        }
                    }
                }
            }
        }
        """
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() 

        data = response.json()
        
        review_summary = data.get("data", {}).get("related_product_review_summary", {})
        review_count = review_summary.get("all_count", 0)
        star_score = review_summary.get("ratings_average", 0.0)

        return {
            "review_count": review_count,
            "star_score": star_score
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP 리뷰 수 요청 에러: {e}")
    except Exception as e:
        logging.error(f"리뷰 수 요청 오류 발생: {e}")
        return None


    
def extract_product_info(json_data, product_num, product_url):
    return {
        'name': json_data.get('goodsNm', 'N/A'),
        'brand': json_data.get('brandInfo', {}).get('brandName', 'N/A'),
        'parent_category': json_data.get('category', {}).get('categoryDepth1Title', 'N/A'),
        'category': json_data.get('category', {}).get('categoryDepth2Title', 'N/A'),
        'product_num': product_num,
        'current_price': json_data.get('goodsPrice', {}).get('salePrice', 'N/A'),
        'image_url': json_data.get('thumbnailImageUrl', 'N/A'),
        'star_score': json_data.get('goodsReview', {}).get('satisfactionScore', 'N/A'),
        'review_count': json_data.get('goodsReview', {}).get('totalCount', 'N/A'),
        'product_url': product_url,
        'brand_logo_url': json_data.get('brandInfo', {}).get('brandLogoImage', 'N/A'),
        'like_count': 0,  # 현재 like_count는 가상 데이터
    }

def parsing_product_to_json_data(product_num, session, headers, product_url):
    response = session.get(product_url, headers=headers, timeout=5)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'lxml')
    

    script_data = soup.find('script', {'id': '__NEXT_DATA__'})
    if not script_data:
        logging.warning(f'상품 정보를 찾을 수 없습니다. 상품 번호: {product_num}')
        return None

    json_data = json.loads(script_data.string)
    return json_data

def extract_zigzag_product_main_info(product_num, session, headers):
    product_url = f'{ZIGZAG_PRODUCT_URL}/{product_num}'
    
    try:
        json_data = parsing_product_to_json_data(product_num, session, headers, product_url)
        
        product_data = json_data.get('props', {}).get('pageProps', {}).get('product', {})
        brand_data = json_data.get('props', {}).get('pageProps', {}).get('shop', {})
        review_summary = get_review_summary(product_num, headers)
        
        # 카테고리 정보 추출
        managed_categories = product_data.get('managed_category_list', [])
        category_datas = [cat['value'] for cat in managed_categories]
        
        if not product_data:
            logging.warning(f'상품 데이터를 찾을 수 없습다. 상품 번호: {product_num}')
            return None
        
        return {
            'name': product_data.get('name', 'N/A'),
            'brand': brand_data.get('name','N/A'),
            'parent_category': category_datas[2],
            'category': category_datas[3],
            'product_num': product_num,
            'product_url' : product_url,
            'current_price': product_data.get('product_price', {}).get('final_discount_info', {}).get('discount_price', 'N/A'),
            'image_url': product_data.get('product_image_list', [{}])[0].get('url', 'N/A'),
            'star_score': review_summary['star_score'],
            'review_count': review_summary['review_count'],
            'brand_logo_url':brand_data.get('typical_image_url', 'N/A'),
            'like_count': 0,
        }

    except json.JSONDecodeError as e:
        logging.error(f'JSON 파싱 오류: {product_num}, 오류: {e}')
        return None
    
def fetch_product_info_multithread(products_num, headers):
    products_info = []
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            futures = [executor.submit(extract_zigzag_product_main_info, product_num, session, headers) for product_num in products_num]
            for future in futures:
                product_info = future.result()
                if product_info:
                    products_info.append(product_info)
    return products_info

def print_product_main_data(products_info):
    for product_info in products_info:
        print(f'상품 번호: {product_info["product_num"]}')
        print(f'상품 이름: {product_info["name"]}')
        print(f'브랜드: {product_info["brand"]}')
        print(f'상위 카테고리: {product_info["parent_category"]}')
        print(f'카테고리: {product_info["category"]}')
        print(f'상품 판매가: {product_info["current_price"]}')
        print(f'상품 URL: {product_info["product_url"]}')
        print(f'상품 이미지 URL: {product_info["image_url"]}')
        print(f'좋아요 수: {product_info["like_count"]}')
        print(f'별점: {product_info["star_score"]}')
        print(f'리뷰 수: {product_info["review_count"]}')
        print(f'로고 URL: {product_info["brand_logo_url"]}')
        print("---------------------------------------")

def get_zigzag_product_info():
    products_num = read_product_numbers(ZIGZAG_PRODUCTS_FILE_PATH)
    
    headers = {
        'User-Agent': USER_AGENT,
        "Connection": "close"
    }
 
    start_time = time.time()
    products_info = fetch_product_info_multithread(products_num, headers)
    end_time = time.time()
    
    logging.info(f'총 실행 시간: {end_time - start_time:.2f}초')
    print_product_main_data(products_info)
    
    # DB에 저장
    save_product_info(products_info, ShopType.ZIGZAG)


if __name__ == "__main__":
    get_zigzag_product_info()

