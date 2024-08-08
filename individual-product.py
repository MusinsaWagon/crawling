import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor
from driver_setup import setup_driver  
from multiprocessing import Pool, cpu_count
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from config.mysql import Session, Product
import logging
from config.log import *

load_dotenv() # 환경변수 로딩

# 무신사 상품 기본 URL
MUSINSA_PRODUCT_URL = os.getenv("MUSINSA_PRODUCT_URL")
LOG_FILE = os.getenv("LOG_FILE")
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

def save_to_database(products_info):
    session = Session()
    try:
        with session.begin():
            for product in products_info:
                new_product = Product(
                    name=product['name'],
                    brand=product['brand'],
                    category_id=1,  # 예시로 카테고리 ID를 1로 설정
                    product_id=int(product['product_id']),
                    img_url=product['image_url'],
                    product_url=product['product_url'],
                    current_price=int(product['current_price']) if product['current_price'] != 'N/A' else 0
                )
                session.add(new_product)
    except Exception as e:
        session.rollback()
        logging.error(f"초기 상품 저장 오류: {e}")
    
def extract_product_info(soup, product_num):
    name_tag = soup.find('h2', class_='sc-1pxf5ii-2 fIpPKc')
    name = name_tag.get_text(strip=True) if name_tag else 'N/A'

    brand_tag = soup.find('a', class_="sc-18j0po5-6")
    brand = brand_tag.get_text(strip=True) if brand_tag else 'N/A'

    price_tag = soup.find('span', class_='sc-f0xecg-5')
    if price_tag:
        price_text = price_tag.get_text(strip=True).replace(',', '').replace('원', '')
        prices = [int(price) for price in price_text.split('~')]
        price = str(max(prices))
    else:
        price = 'N/A'

    img_tag = soup.find('img', class_='sc-1jl6n79-4')
    img_url = img_tag['src'] if img_tag else 'N/A'

    like_tag = soup.find('span', class_='cIxZGm')
    like_text = like_tag.get_text(strip=True).replace(',', '') if like_tag else 'N/A'
    like_count = ''.join(filter(str.isdigit, like_text))  # 숫자만 추출

    return {
        'name': name,
        'brand': brand,
        'product_id' : product_num,
        'current_price': price,
        'like_count': like_count,
        'image_url': img_url,
        'product_url' : MUSINSA_PRODUCT_URL + "/" + product_num,
    }

def get_individual_product_info(chromedriver_path, product_num):
    product_url = f'{MUSINSA_PRODUCT_URL}/{product_num}'
    driver = setup_driver(chromedriver_path)
    
    try:
        driver.get(product_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'sc-1pxf5ii-2'))  # 이름 요소 기다림
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'cIxZGm')) # 좋아요 요소 기다림
        )

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        product_info = extract_product_info(soup, product_num)
    
        return product_info

    finally:
        driver.quit()

def fetch_product_info_multithread(products_num, chromedriver_path):
    products_info = []  # 상품 정보를 저장할 리스트
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_individual_product_info, chromedriver_path, product_num) for product_num in products_num]
        for future in futures:
            product_info = future.result()
            products_info.append(product_info)  # 결과를 리스트에 추가
        
    return products_info

def fetch_product_info_multiprocess(products_num, chromedriver_path):
    with Pool(processes=cpu_count()) as pool:
        product_info_list = pool.starmap(get_individual_product_info, [(chromedriver_path, product) for product in products_num])
    return product_info_list

    
def print_product_data(products_info):
    # 결과 출력
    for product_info in products_info:
        logging.info(f'상품 번호: {product_info["product_id"]}')
        logging.info(f'상품 이름: {product_info["name"]}')
        logging.info(f'브랜드: {product_info["brand"]}')
        logging.info(f'상품 가격: {product_info["current_price"]}')
        logging.info(f'상품 URL: {product_info["product_url"]}')
        logging.info(f'상품 이미지 URL: {product_info["image_url"]}')
        logging.info(f'좋아요 수: {product_info["like_count"]}')
        logging.info("---------------------------------------")

def read_product_numbers(file_path):
    try:
        with open(file_path, 'r') as file:
            products_num = [line.strip() for line in file if line.strip().isdigit()]
        return products_num
    except FileNotFoundError:
        logging.error(f"파일을 찾을 수 없습니다: {file_path}")
        return []
    
def main():
    products_num = read_product_numbers(f'{PRODUCTS_FILE_PATH}')
    chromedriver_path = f'{CHROMEDRIVER_PATH}'
 
    start_time = time.time()  # 시작 시간 기록
    product_info = fetch_product_info_multithread(products_num, chromedriver_path)
    print_product_data(product_info)
    end_time = time.time()
    logging.info(f'총 실행 시간: {end_time - start_time:.2f}초')  # 실행 시간 계산 및 출력

    save_to_database(product_info)
    
if __name__ == "__main__":
    main()
