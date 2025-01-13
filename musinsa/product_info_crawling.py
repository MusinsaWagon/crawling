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


# 무신사 상품 기본 URL
USER_AGENT = os.getenv("USER_AGENT")
MUSINSA_PRODUCT_URL = os.getenv("MUSINSA_PRODUCT_URL")
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH")

load_dotenv() # 환경변수 로딩
   
def extract_json_from_script(script_content):
    json_start = script_content.find('{"goodsNo":')
    json_end = script_content.rfind('}') + 1
    if json_start != -1 and json_end != -1:
        return json.loads(script_content[json_start:json_end])
    return None

    
def extract_musinsa_product_main_info(product_num, session, headers):
    product_url = f'{MUSINSA_PRODUCT_URL}/{product_num}'
    
    try:
        response = session.get(product_url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        script_tag = soup.find('script', string=lambda t: t and 'window.__MSS__.product.state' in t)
        if not script_tag:
            logging.warning(f'상품 정보를 찾을 수 없습니다. 상품 번호: {product_num}')
            return None

        script_content = script_tag.string.strip()
        json_data = extract_json_from_script(script_content)
        if not json_data:
            logging.warning(f'JSON 데이터를 추출할 수 없습니다. 상품 번호: {product_num}')
            return None

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

    except requests.RequestException as e:
        logging.error(f'페이지를 불러오지 못했습니다. 상품 번호: {product_num}, 오류: {e}')
        return None
    
def fetch_product_info_multithread(products_num, headers):
    products_info = []
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            futures = [executor.submit(extract_musinsa_product_main_info, product_num, session, headers) for product_num in products_num]
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

def get_musinsa_product_info():
    products_num = read_product_numbers(PRODUCTS_FILE_PATH)
    
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
    save_product_info(products_info, ShopType.MUSINSA)

if __name__ == "__main__":
    get_musinsa_product_info()

