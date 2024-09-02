from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from dotenv import load_dotenv
from config.driver_setup import setup_driver

# 현재 스크립트의 디렉터리 경로 가져오기
script_dir = os.path.dirname(os.path.abspath(__file__))

# 상대 경로를 기반으로 파일의 절대 경로 생성
file_path = os.path.join(script_dir, '..', 'musinsa_product_ids.txt')

load_dotenv()  # 환경변수 로딩

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

def get_products_id(product):
    product_id = product.get_attribute('data-item-id') 
    return {
        'Product_ID': product_id
    }

def scroll_and_load_products(driver, url, target_count=100):
    product_list = []
    seen_ids = set()  # 중복 방지를 위한 Set

    driver.get(url)
    time.sleep(2)
    while len(product_list) < target_count:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 새로운 상품이 로드될 때까지 잠시 대기

        products = driver.find_elements(By.CSS_SELECTOR, 'a[data-item-id]')
        
        for product in products:
            product_info = get_products_id(product)
            product_id = product_info['Product_ID']
            if product_id not in seen_ids:
                seen_ids.add(product_id)
                product_list.append(product_info)
        
        if len(product_list) >= target_count:
            break  # 목표 개수에 도달하면 종료
    
    return product_list[:target_count]

def extract_product_num_from_categoryinfo():
    base_url = 'https://www.musinsa.com/categories/item/'
    category_ids = ['001005', '001002', '001004',
                   '002022', '002001', '002002', 
                   '003004', '003009', '003008', 
                   '100001', '100003']# 크롤링 할 카테고리 ID
    item_count = 8  # 크롤링 할 상품의 수
    chromedriver_path = f'{CHROMEDRIVER_PATH}'
    driver = setup_driver(chromedriver_path)
    
    all_ids = []  # 상품 ID를 저장할 리스트
    
    try:
        for category_id in category_ids:
            url = f'{base_url}{category_id}?gf=A&sortCode=SALE_ONE_YEAR_COUNT'
            print(f'Crawling URL: {url}')
            
            product_list = scroll_and_load_products(driver, url, item_count)
            
            # 상품 ID 추출
            for product in product_list:
                all_ids.append(product['Product_ID'])

        # 상품 ID를 텍스트 파일에 숫자만 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            for product_id in all_ids:
                f.write(f"{product_id}\n")
    
    finally:
        driver.quit()

extract_product_num_from_categoryinfo()