import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
import time
import logging
from config.log import *
from config.slack import send_result_to_slack
from config.file import read_product_numbers
from models.product import update_product_and_history_and_detail_info, get_all_product_numbers
import random
import re
from models.shop_type import ShopType

load_dotenv()

# 무신사 상품 기본 URL
MUSINSA_PRODUCT_URL = os.getenv("MUSINSA_PRODUCT_URL")
USER_AGENT = os.getenv("USER_AGENT")
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH")

# 페이지 소스에서 가격 정보 가져오기
def extract_musinsa_current_price(product_num, headers):
   
    product_url = f'{MUSINSA_PRODUCT_URL}/{product_num}'
    
    try:
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        # script 태그에서 JavaScript 객체를 추출
        script_tag = soup.find('script', string=lambda t: t and 'window.__MSS__.product.state' in t)

        if script_tag:
             # script 내용 중 필요한 부분만 추출
            script_content = script_tag.string.strip()
            # 정규식으로 JSON 추출
            match = re.search(r'window\.__MSS__\.product\.state\s*=\s*({.*?});', script_content)
            if match:
                json_str = match.group(1)  # 첫 번째 그룹이 JSON 문자열
                json_data = json.loads(json_str)
                current_price = json_data.get('goodsPrice', {}).get('salePrice', 'N/A')
                return current_price
            else:
                logging.warning(f'JSON 데이터를 추출할 수 없습니다. 상품 번호: {product_num}')
                return None
        else:
            logging.warning(f'상품 가격 정보를 찾을 수 없습니다. 상품 번호: {product_num}')
            return None
        
    except requests.RequestException as e:
        logging.error(f'페이지를 불러오지 못했습니다. 상품 번호: {product_num}, 오류: {e}')
        return None

# 상품 가격 추출
def process_products(products_num):
    headers = get_headers()
    successful_products = []
    failed_products = []
    
    for product_id in products_num:
        time.sleep(random.uniform(1, 3))  # 1초에서 3초 사이의 랜덤 딜레이
        
        price = extract_musinsa_current_price(product_id, headers)
        if price:
            successful_products.append(f'상품 번호: {product_id}, 가격: {price}원')
            update_product_and_history_and_detail_info(price, product_id, "MUSINSA")
        else:
            failed_products.append(product_id)
    
    return successful_products, failed_products

def get_headers():
    return {
        'User-Agent': f'{USER_AGENT}',
        "Connection": "close"
    }

# 하루마다 상품 가격 받아오기
def get_product_day_price():
    products_num = get_all_product_numbers(ShopType.MUSINSA)
    # products_num = read_product_numbers(PRODUCTS_FILE_PATH)
    
    if not products_num:
        logging.warning("상품 번호가 없습니다. 프로그램을 종료합니다.")
        return

    start_time = time.time()
    successful_products, failed_products = process_products(products_num)
    end_time = time.time()
    
    logging.info(f'Day_Price 실행 시간: {end_time - start_time:.2f}초')
    send_result_to_slack(products_num, successful_products, failed_products)

def main():
    get_product_day_price()

if __name__ == "__main__":
    main()