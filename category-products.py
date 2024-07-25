import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
from bs4 import BeautifulSoup
import re

def setup_driver(chromedriver_path):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 표시하지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_product_info(product):
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
        'Name': name,
        'Brand': brand,
        'Price': price,
        'Like' : like,
        'Image_URL': img_url
    }

def scroll_and_load_products(driver, target_count=100):
    product_list = []
    while len(product_list) < target_count:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 새로운 상품이 로드될 때까지 잠시 대기

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        products = soup.select('div.category__sc-rb2kzk-0.irgXw')
        
        new_products = [extract_product_info(product) for product in products[len(product_list):]]
        product_list.extend(new_products)

        if len(new_products) == 0:
            break  # 더 이상 로드할 상품이 없으면 종료
    
    return product_list[:target_count]

def main():
    url = 'https://www.musinsa.com/categories/item/002025?device=mw&sortCode=1y'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(current_dir, 'chromedriver')
    driver = setup_driver(chromedriver_path)
    
    try:
        driver.get(url)
        time.sleep(5)  # 초기 페이지 로드 대기

        product_list = scroll_and_load_products(driver)

        df = pd.DataFrame(product_list)
        print(df)
        df.to_excel('musinsa_top_100_products.xlsx', index=False)
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()