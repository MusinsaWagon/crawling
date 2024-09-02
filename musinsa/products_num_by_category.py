from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import time
from dotenv import load_dotenv
from config.driver_setup import setup_driver
import os

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

    driver.get(url)
    time.sleep(2)
    while len(product_list) < target_count:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 새로운 상품이 로드될 때까지 잠시 대기

        products = driver.find_elements(By.CSS_SELECTOR, 'div.sc-dtBeHJ.iFyEFD a[data-item-id]')
        
        for product in products:
            print(product.get_attribute('data-item-id') + "\n" )
            
        # 새로운 상품만 추가
        new_products = [get_products_id(product) for product in products]
        print(new_products)
        product_list.extend(new_products)

        if len(new_products) == 0:
            break  # 더 이상 로드할 상품이 없으면 종료
    
    return product_list[:target_count]

def extract_product_num_from_categoryinfo():
    base_url = 'https://www.musinsa.com/categories/item/'
    category_ids = ['001005']
    # category_ids = ['003002']
    item_count = 8  # 크롤링 할 상품의 수
    chromedriver_path = f'{CHROMEDRIVER_PATH}'
    driver = setup_driver(chromedriver_path)
    
    all_products = []
    all_ids = []  # 상품 ID를 저장할 리스트
    
    try:
        for category_id in category_ids:
            url = f'{base_url}{category_id}?gf=A&sortCode=SALE_ONE_YEAR_COUNT'
            print(f'Crawling URL: {url}')
            
            product_list = scroll_and_load_products(driver, url, item_count)
            all_products.extend(product_list)
            
            # 상품 ID 추출
            for product in product_list:
                all_ids.append(product['Product_ID'])

        # 상품 ID를 텍스트 파일에 숫자만 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            for product_id in all_ids:
                f.write(f"{product_id}\n")
    
    finally:
        driver.quit()

