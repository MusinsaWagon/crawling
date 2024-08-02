import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor
from driver_setup import setup_driver  


def extract_product_info(soup, product_url):
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
        'Name': name,
        'Brand': brand,
        'Product_URL' : product_url,
        'Price': price,
        'Like': like_count,
        'Image_URL': img_url
    }

def get_individual_product_info(chromedriver_path, product_num):
    product_url = f'https://www.musinsa.com/app/goods/{product_num}'
    driver = setup_driver(chromedriver_path)
    
    try:
        driver.get(product_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'sc-1pxf5ii-2'))  # 원하는 요소의 클래스 이름
        )

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        product_info = extract_product_info(soup, product_url)
    
        return product_info

    finally:
        driver.quit()

def fetch_product_info(products_num, chromedriver_path):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(get_individual_product_info, chromedriver_path, product) for product in products_num]
        for future in futures:
            product_info = future.result()
            # 결과 출력
            print(f'상품 이름: {product_info["Name"]}')
            print(f'브랜드: {product_info["Brand"]}')
            print(f'상품 가격: {product_info["Price"]}')
            print(f'상품 URL: {product_info["Product_URL"]}')
            print(f'상품 이미지 URL: {product_info["Image_URL"]}')
            print(f'좋아요 수: {product_info["Like"]}')

def read_product_numbers(file_path):
    with open(file_path, 'r') as file:
        products_num = [line.strip() for line in file if line.strip().isdigit()]
    return products_num

def main():
    products_file = 'individual_products.txt'
    products_num = read_product_numbers(products_file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(current_dir, 'chromedriver')
    
    start_time = time.time()  # 시작 시간 기록
    fetch_product_info(products_num, chromedriver_path)
    end_time = time.time()
    print(f'총 실행 시간: {end_time - start_time:.2f}초')  # 실행 시간 계산 및 출력

if __name__ == "__main__":
    main()