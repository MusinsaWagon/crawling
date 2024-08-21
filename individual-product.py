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

def extract_musinsa_product_main_info(driver, product_num):
    
    # 페이지 로딩 대기
    wait = WebDriverWait(driver, 5)
    
     # 제품 이름
    try:
        name_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[1]/div[2]/div[4]/span')))
        name = name_element.text.strip()
    except:
        name = 'N/A'
        
    # 브랜드 이름
    try:
        brand_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[1]/div[2]/div[1]/div/a/div[2]/span[1]')))
        brand = brand_element.text.strip()
    except:
        brand = 'N/A'

    # 카테고리 정보
    try:
        category_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="root"]/div[1]/div[2]/div[3]/div')))
       
        category_text = category_elements[0].text.strip()
        categories = category_text.split('\n')  # 줄바꿈을 기준으로 분리

        parent_category = categories[0] if len(categories) > 0 else 'N/A'
        category = categories[1] if len(categories) > 1 else 'N/A'
    except:
        parent_category = 'N/A'
        category = 'N/A'
        

    # 할인된 가격 (sale_price)
    try:
        sale_price_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[1]/div[2]/div[8]/div/div/div/span[2]')))
        sale_price = int(sale_price_element.text.strip().replace(',', '').replace('원', ''))
    except:
        sale_price = 'N/A'

    # 원래 가격 (origin_price)
    try:
        origin_price_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[1]/div[2]/div[8]/div/div/span')))
        origin_price = int(origin_price_element.text.strip().replace(',', '').replace('원', ''))
    except:
        origin_price = 'N/A'


    # 이미지 URL
    try:
        img_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[1]/div[1]/div/div[1]/div/div[1]/div/div[1]/img')))
        img_url = img_element.get_attribute('src')
    except:
        img_url = 'N/A'


    return {
        'name': name,
        'brand': brand,
        'parent_category' : parent_category,
        'category' : category,
        'product_id' : product_num,
        'sale_price': sale_price,
        'origin_price' : origin_price,
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
    
    
def extract_product_info(driver, product_num):
    noraml_info = extract_musinsa_product_main_info(driver, product_num) # 메인 정보 가져오기
    # side_info = extract_musinsa_product_side_info(driver, product_num) # 좋아요, 별점등 사이
    
    # noraml_info.update(side_info)
    
    return noraml_info

def get_individual_product_info(chromedriver_path, product_num):
    product_url = f'{MUSINSA_PRODUCT_URL}/{product_num}'
    driver = setup_driver(chromedriver_path)
    
    try:
        driver.get(product_url)
    
        product_info = extract_product_info(driver, product_num) # 상품정보 가져오기
    
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
        logging.info(f'상품 원가: {product_info["origin_price"]}')
        logging.info(f'상품 판매가: {product_info["sale_price"]}')
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
    
    print_product_main_data(product_info)
    # print_product_side_data(product_info)
    # save_product_info(product_info)
    
if __name__ == "__main__":
    main()
