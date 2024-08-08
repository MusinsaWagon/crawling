import requests
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
import time
import logging
from config.log import *

load_dotenv()  # 환경변수 로딩

# 무신사 상품 기본 URL
MUSINSA_PRODUCT_URL = os.getenv("MUSINSA_PRODUCT_URL")
USER_AGENT = os.getenv("USER_AGENT")
LOG_FILE = os.getenv("LOG_FILE")
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH")

def read_product_numbers(file_path):
    try:
        with open(file_path, 'r') as file:
            products_num = [line.strip() for line in file if line.strip().isdigit()]
        return products_num
    except FileNotFoundError:
        logging.error(f"파일을 찾을 수 없습니다: {file_path}")
        return []

def fetch_price(product_id, headers):
    product_url = f'{MUSINSA_PRODUCT_URL}/{product_id}'
    try:
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')
        script_tag = soup.find('script', type='application/ld+json')
        
        if script_tag:
            json_data = json.loads(script_tag.string)
            price = json_data.get('offers', {}).get('price', 'N/A')
            return price
        else:
            logging.warning(f'가격 정보를 찾을 수 없습니다. 상품 번호: {product_id}')
            return 'N/A'
    except requests.RequestException as e:
        logging.error(f'페이지를 불러오지 못했습니다. 상품 번호: {product_id}, 오류: {e}')
        return 'N/A'

def main():
    products_num = read_product_numbers(f'{PRODUCTS_FILE_PATH}')
    
    if not products_num:
        logging.info("상품 번호가 없습니다. 프로그램을 종료합니다.")
        return
    
    headers = {
        'User-Agent': f'{USER_AGENT}',
        "Connection": "close"
    }
    
    start_time = time.time()  
    
    for product_id in products_num:
        price = fetch_price(product_id, headers)
        logging.info(f'상품 번호: {product_id}, 상품 가격: {price}원')
        
    end_time = time.time()
    logging.info(f'총 실행 시간: {end_time - start_time:.2f}초') 

if __name__ == "__main__":
    main()