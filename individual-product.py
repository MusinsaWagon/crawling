import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import os
import re

def setup_driver(chromedriver_path):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 표시하지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_product_info(soup):
    name_tag = soup.find('h2', class_='sc-1pxf5ii-2 fIpPKc')
    name = name_tag.get_text(strip=True) if name_tag else 'N/A'

    brand_tag = soup.find('a', class_="sc-18j0po5-6")
    brand = brand_tag.get_text(strip=True) if brand_tag else 'N/A'

    price_tag = soup.find('span', class_='sc-f0xecg-5')
    price = price_tag.get_text(strip=True).replace(',', '').replace('원', '') if price_tag else 'N/A'

    img_tag = soup.find('img', class_='sc-1jl6n79-4')
    img_url = img_tag['src'] if img_tag else 'N/A'

    soup.select_one('img')['src']
    like_tag = soup.find('span', class_='cIxZGm')
    like_text = like_tag.get_text(strip=True).replace(',', '') if like_tag else 'N/A'
    like_count = ''.join(filter(str.isdigit, like_text))  # 숫자만 추출

    return {
        'Name': name,
        'Brand': brand,
        'Price': price,
        'Like' : like_count,
        'Image_URL': img_url
    }

def main():
    url = 'https://www.musinsa.com/app/goods/3135346'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(current_dir, 'chromedriver')
    driver = setup_driver(chromedriver_path)
    
    try:
        driver.get(url)
        time.sleep(3)  # 페이지가 완전히 로드될 때까지 대기

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        product_info = extract_product_info(soup)
        
        # 결과 출력
        print(f'상품 이름: {product_info["Name"]}')
        print(f'브랜드: {product_info["Brand"]}')
        print(f'상품 가격: {product_info["Price"]} 원')
        print(f'상품 이미지 URL: {product_info["Image_URL"]}')
        print(f'좋아요 수: {product_info["Like"]}')

    finally:
        driver.quit()

if __name__ == "__main__":
    main()