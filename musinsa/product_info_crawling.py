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

load_dotenv() # 환경변수 로딩

# 무신사 상품 기본 URL
USER_AGENT = os.getenv("USER_AGENT")
MUSINSA_PRODUCT_URL = os.getenv("MUSINSA_PRODUCT_URL")
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH")
ADD_PROUDCTS_LIST_FILE_PATH = os.getenv("ADD_PROUDCTS_LIST_FILE_PATH")
   
def extract_musinsa_product_main_info(product_num, session, headers):
  
    product_url = f'{MUSINSA_PRODUCT_URL}/{product_num}'
    
    try:
        response = session.get(product_url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        # script 태그에서 JavaScript 객체를 추출
        script_tag = soup.find('script', string=lambda t: t and 'window.__MSS__.product.state' in t)

        if script_tag:
             # script 내용 중 필요한 부분만 추출
            script_content = script_tag.string.strip()

            # JSON 객체만 추출
            json_start = script_content.find('{"goodsNo":')
            json_end = script_content.rfind('}') + 1

            # JSON 데이터가 올바르게 추출되었는지 확인
            if json_start != -1 and json_end != -1:
                json_data = json.loads(script_content[json_start:json_end])

                # 필요한 정보 추출
                name = json_data.get('goodsNm', 'N/A')
                brand = json_data.get('brandInfo', {}).get('brandName', 'N/A')
                parent_category = json_data.get('category', {}).get('categoryDepth1Title', 'N/A')
                category = json_data.get('category', {}).get('categoryDepth2Title', 'N/A')
                current_price = json_data.get('goodsPrice', {}).get('memberPrice', 'N/A')
                img_url = json_data.get('thumbnailImageUrl', 'N/A')
                star_score = json_data.get('goodsReview', {}).get('satisfactionScore', 'N/A')
                review_count = json_data.get('goodsReview', {}).get('totalCount', 'N/A')

                return {
                    'name': name,
                    'brand': brand,
                    'parent_category': parent_category,
                    'category': category,
                    'product_num': product_num,
                    'current_price': current_price,
                    'image_url': img_url,
                    'star_score': star_score,
                    'review_count': review_count,
                    'product_url': product_url,
                    'like_count': 0,  # 현재 like_count는 가상 데이터
                }
            else:
                logging.warning(f'JSON 데이터를 추출할 수 없습니다. 상품 번호: {product_num}')
                return None
        else:
            logging.warning(f'상품 정보를 찾을 수 없습니다. 상품 번호: {product_num}')
            return None
        
    except requests.RequestException as e:
        logging.error(f'페이지를 불러오지 못했습니다. 상품 번호: {product_num}, 오류: {e}')
        return None


def fetch_product_info_multithread(products_num, headers):
    products_info = []  # 상품 정보를 저장할 리스트
    with requests.Session() as session:  # 세션을 재사용하여 속도 향상
        with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            futures = [executor.submit(extract_musinsa_product_main_info, product_num , session, headers) for product_num in products_num]
            for future in futures:
                product_info = future.result()
                if product_info:
                    products_info.append(product_info)  # 결과를 리스트에 추가
                    
    return products_info


def print_product_main_data(products_info):
    # 결과 출력
    for product_info in products_info:
       print(f'상품 번호: {product_info["product_num"]}')
       print(f'상품 이름: {product_info["name"]}')
       print(f'브랜드: {product_info["brand"]}')
       print(f'상위 카테고리: {product_info["parent_category"]}')
       print(f'카테고리: {product_info["category"]}')
       print(f'상품 판매가: {product_info["current_price"]}')
       print(f'상품 URL: {product_info["product_url"]}')
       print(f'상품 이미지 URL: {product_info["image_url"]}')
       print("---------------------------------------")
       print(f'좋아요 수: {product_info["like_count"]}')
       print(f'별점: {product_info["star_score"]}')
       print(f'리뷰 수: {product_info["review_count"]}')
       print("---------------------------------------")
        

    
def get_musinsa_product_info():
    products_num = read_product_numbers(f'{PRODUCTS_FILE_PATH}')
    
    headers = {
        'User-Agent': f'{USER_AGENT}',
        "Connection": "close"
    }
 
    start_time = time.time()  # 시작 시간 기록
    products_info = fetch_product_info_multithread(products_num, headers)
    end_time = time.time()
    
    print_product_main_data(products_info)
    print(f'총 실행 시간: {end_time - start_time:.2f}초')  # 실행 시간 계산 및 출력
    
    save_product_info(products_info)
    
