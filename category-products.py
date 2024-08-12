import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
from bs4 import BeautifulSoup
import re
from driver_setup import setup_driver   
from dotenv import load_dotenv

load_dotenv() # 환경변수 로딩
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

def extract_product_info(product):
    product_id = product.get('data-goodsno', 'N/A')
    
    name_tag = product.select_one('div[class*="category__sc-rb2kzk-10"] a:nth-of-type(2)')
    name = name_tag.get_text(strip=True) if name_tag else 'N/A'

    brand_tag = product.select_one('div[class*="category__sc-rb2kzk-10"] a:nth-of-type(1)')
    brand = brand_tag.get_text(strip=True) if brand_tag else 'N/A'

    price_tag = product.select_one('div[class*="category__sc-79f6w4-4"] span')
    price = price_tag.get_text(strip=True).replace(',', '').split('원')[0] if price_tag else 'N/A'

    like_tag = product.select_one('div[class*="category__sc-rb2kzk-15"]')
    if like_tag:
        like_text = like_tag.get_text(strip=True).replace(',', '')
        like = re.search(r'\d+', like_text).group() if re.search(r'\d+', like_text) else 'N/A'
    else:
        like = 'N/A'
        
    img_tag = product.select_one('img')
    img_url = img_tag['src'] if img_tag else 'N/A'

    return {
        'Product_id': product_id,
        'Name': name,
        'Brand': brand,
        'Price': price,
        'Like' : like,
        'Image_URL': img_url
    }
    
def get_products_id(product):
    product_id = product.get('data-goodsno', 'N/A')
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

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        products = soup.select('div.category__sc-rb2kzk-0.irgXw')
        
        new_products = [get_products_id(product) for product in products[len(product_list):]]
        product_list.extend(new_products)
        

        if len(new_products) == 0:
            break  # 더 이상 로드할 상품이 없으면 종료
    
    return product_list[:target_count]

def main():
    base_url = 'https://www.musinsa.com/categories/item/'
    category_ids = ['001005', '001002', '001004', '001006','001003', '001010', '001001','001011', '001013', '001008']  
    item_count = 120 # 크롤링 할 상품의 수
    chromedriver_path = f'{CHROMEDRIVER_PATH}'
    driver = setup_driver(chromedriver_path)
    
    all_products = []
    all_ids = []  # 상품 ID를 저장할 리스트
    
    try:
        for category_id in category_ids:
            url = f'{base_url}{category_id}?device=mw&sortCode=1y'
            print(f'Crawling URL: {url}')
            
            product_list = scroll_and_load_products(driver, url, item_count)
            all_products.extend(product_list)
            
            # 상품 ID 추출
            for product in product_list:
                all_ids.append(product['Product_ID'])

        # DataFrame 저장
        df = pd.DataFrame(all_products)
        df.to_excel('musinsa_top_100_products.xlsx', index=False)

        # 상품 ID를 텍스트 파일에 숫자만 저장
        with open('musinsa_product_ids.txt', 'w', encoding='utf-8') as f:
            for product_id in all_ids:
                f.write(f"{product_id}\n")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
