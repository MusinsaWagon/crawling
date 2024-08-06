import requests
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
import time


load_dotenv() # 환경변수 로딩

# 무신사 상품 기본 URL
MUSINSA_PRODUCT_URL = os.getenv("MUSINSA_PRODUCT_URL")

def read_product_numbers(file_path):
    with open(file_path, 'r') as file:
        products_num = [line.strip() for line in file if line.strip().isdigit()]
    return products_num

def fetch_price(product_id, headers):
    product_url = f'{MUSINSA_PRODUCT_URL}/{product_id}'

    response = requests.get(product_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        script_tag = soup.find('script', type='application/ld+json')
        
        if script_tag:
            json_data = json.loads(script_tag.string)
            price = json_data.get('offers', {}).get('price', 'N/A')
            return price
        else:
            print(f'가격 정보를 찾을 수 없습니다. 상품 번호: {product_id}')
            return 'N/A'
    else:
        print(f'페이지를 불러오지 못했습니다. 상품 번호: {product_id} 상태 코드: {response.status_code}')
        return 'N/A'

def main():
    products_file = './etc/individual_products.txt'
    products_num = read_product_numbers(products_file)
    
    # 요청 헤더 설정 (User-Agent는 웹 크롤링 방지 설정을 우회하기 위해 필요)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        "Connection": "close"
    }
    
    start_time = time.time()  # 시작 시간 기록
    
    for product_id in products_num:
        price = fetch_price(product_id, headers)
        print(f'상품 번호: {product_id}, 상품 가격: {price}원')
        
    end_time = time.time()
    print(f'총 실행 시간: {end_time - start_time:.2f}초')  # 실행 시간 계산 및 출력


if __name__ == "__main__":
    main()