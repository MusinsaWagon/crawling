import requests
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
import time
import logging
from config.log import *
from config.file import read_product_numbers
from config.slack import send_slack_message
from models.product import update_product_and_history_and_detail_info
import random

load_dotenv()  # 환경변수 로딩

# 무신사 상품 기본 URL
MUSINSA_PRODUCT_URL = os.getenv("MUSINSA_PRODUCT_URL")
USER_AGENT = os.getenv("USER_AGENT")
LOG_FILE = os.getenv("LOG_FILE")
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH")

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

            # JSON 객체만 추출
            json_start = script_content.find('{"goodsNo":')
            json_end = script_content.rfind('}') + 1

            # JSON 데이터가 올바르게 추출되었는지 확인
            if json_start != -1 and json_end != -1:
                json_data = json.loads(script_content[json_start:json_end])

                # 판매가 추출
                current_price = json_data.get('goodsPrice', {}).get('memberPrice', 'N/A')
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
    
def get_product_price():
    products_num = read_product_numbers(f'{PRODUCTS_FILE_PATH}')
    
    headers = {
        'User-Agent': f'{USER_AGENT}',
        "Connection": "close"
    }
    
    if not products_num:
        logging.info("상품 번호가 없습니다. 프로그램을 종료합니다.")
        return

    start_time = time.time()  
    
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
        
        
    end_time = time.time()
    
    logging.info(f'Day_Price 실행 시간: {end_time - start_time:.2f}초') 
    
    # Slack 알림
    total_products = len(products_num)  # 전체 상품 수
    success_count = len(successful_products)  # 성공적으로 추출된 상품 수
    fail_count = len(failed_products)  # 실패한 상품 수
    
    failed_message = ", ".join(failed_products) if failed_products else "모든 상품의 데이터를 성공적으로 추출했습니다."

    result_title = "🌟 상품 가격 추출 결과 🌟"
    result_message = (
        f"총 상품 수: {total_products}\n"
        f"성공적으로 추출된 상품 수: {success_count}\n"
        f"실패한 상품 수: {fail_count}\n\n"
        f"❗️*추출에 실패한 상품들*\n{failed_message}"
    )
    
    send_slack_message(result_title, result_message)
