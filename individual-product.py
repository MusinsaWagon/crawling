import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor
from driver_setup import setup_driver  
from multiprocessing import Pool, cpu_count
from dotenv import load_dotenv
import logging
from config.log import *
from config.mysql import *
from models.product import save_product_info

load_dotenv() # 환경변수 로딩

# 무신사 상품 기본 URL
MUSINSA_PRODUCT_URL = os.getenv("MUSINSA_PRODUCT_URL")
LOG_FILE = os.getenv("LOG_FILE")
PRODUCTS_FILE_PATH = os.getenv("PRODUCTS_FILE_PATH")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

def extract_musinsa_product_main_info(soup, product_num):
    name_tag = soup.find('h2', class_='sc-1pxf5ii-2 fIpPKc')
    name = name_tag.get_text(strip=True) if name_tag else 'N/A'

    brand_tag = soup.find('a', class_="sc-18j0po5-6")
    brand = brand_tag.get_text(strip=True) if brand_tag else 'N/A'

    category_tags = soup.find_all('a', class_="sc-887fco-1")
    
    parent_category = category_tags[0].get_text(strip=True) if len(category_tags) > 0 else 'N/A'
    category = category_tags[1].get_text(strip=True) if len(category_tags) > 1 else 'N/A'
    
    price_tag = soup.find('span', class_='sc-f0xecg-5')
    if price_tag:
        price_text = price_tag.get_text(strip=True).replace(',', '').replace('원', '')
        prices = [int(price) for price in price_text.split('~')]
        price = str(max(prices))
    else:
        price = 'N/A'

    img_tag = soup.find('img', class_='sc-1jl6n79-4')
    img_url = img_tag['src'] if img_tag else 'N/A'

    return {
        'name': name,
        'brand': brand,
        'parent_category' : parent_category,
        'category' : category,
        'product_id' : product_num,
        'current_price': price,
        'image_url': img_url,
        'product_url' : MUSINSA_PRODUCT_URL + "/" + product_num,
    }

def extract_musinsa_product_side_info(soup, product_num):
    like_tag = soup.find('span', class_='cIxZGm')
    like_text = like_tag.get_text(strip=True).replace(',', '') if like_tag else 'N/A'
    like_count = ''.join(filter(str.isdigit, like_text))  # 숫자만 추출
    
    star_tag = soup.find('p', class_='sc-qc190r-3')
    star_count = float(star_tag.get_text(strip=True)) if star_tag else 0.0
    
    review_tag = soup.find('p', class_='sc-qc190r-4 jmQzBL')
    review_count = ''.join(filter(str.isdigit, review_tag.get_text(strip=True))) if review_tag else '0'
    review_count = int(review_count) if review_count else 0
    
    return {
        'like_count' : like_count,
        'star_count' : star_count,
        'review_count' : review_count
    }
    
    
def extract_product_info(soup, product_num):
    noraml_info = extract_musinsa_product_main_info(soup, product_num)
    side_info = extract_musinsa_product_side_info(soup, product_num)
    
    noraml_info.update(side_info)
    
    return noraml_info

def get_individual_product_info(chromedriver_path, product_num):
    product_url = f'{MUSINSA_PRODUCT_URL}/{product_num}'
    driver = setup_driver(chromedriver_path)
    
    try:
        driver.get(product_url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'sc-1pxf5ii-2'))  # 이름 요소 기다림
        )
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'cIxZGm')) # 좋아요 요소 기다림
        )

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        product_info = extract_product_info(soup, product_num)
    
        return product_info
    
    except Exception as e:
        logging.error(f'Error fetching product {product_num}: {str(e)}')
        return None
    finally:
        driver.quit()


def fetch_product_info_multithread(products_num, chromedriver_path):
    products_info = []  # 상품 정보를 저장할 리스트
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        futures = [executor.submit(get_individual_product_info, chromedriver_path, product_num) for product_num in products_num]
        for future in futures:
            product_info = future.result()
            if product_info:
                products_info.append(product_info)  # 결과를 리스트에 추가
                
    return products_info


def fetch_product_info_multiprocess(products_num, chromedriver_path):
    with Pool(processes=cpu_count()) as pool:
        product_info_list = pool.starmap(get_individual_product_info, [(chromedriver_path, product) for product in products_num])
    return product_info_list
    

def print_product_main_data(products_info):
    # 결과 출력
    for product_info in products_info:
        logging.info(f'상품 번호: {product_info["product_id"]}')
        logging.info(f'상품 이름: {product_info["name"]}')
        logging.info(f'브랜드: {product_info["brand"]}')
        logging.info(f'상위 카테고리: {product_info["parent_category"]}')
        logging.info(f'카테고리: {product_info["category"]}')
        logging.info(f'상품 가격: {product_info["current_price"]}')
        logging.info(f'상품 URL: {product_info["product_url"]}')
        logging.info(f'상품 이미지 URL: {product_info["image_url"]}')
        logging.info("---------------------------------------")
        
def print_product_side_data(products_info):
    for product_info in products_info:
        logging.info(f'좋아요 수: {product_info["like_count"]}')
        logging.info(f'별점: {product_info["star_count"]}')
        logging.info(f'리뷰 수: {product_info["review_count"]}')
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
    end_time = time.time()
    logging.info(f'총 실행 시간: {end_time - start_time:.2f}초')  # 실행 시간 계산 및 출력
    
    # print_product_main_data(product_info)
    # print_product_side_data(product_info)
    save_product_info(product_info)
    
if __name__ == "__main__":
    main()
    
    
    
    
