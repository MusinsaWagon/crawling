import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
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
        'Product_URL': product_url,
        'Price': price,
        'Like': like_count,
        'Image_URL': img_url
    }

def get_individual_product_info(chromedriver_path, product_num):
    product_url = f'https://www.musinsa.com/app/goods/{product_num}'
    driver = setup_driver(chromedriver_path)
    
    try:
        driver.get(product_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'sc-1pxf5ii-2'))  # 이름 요소 기다림
        )
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'cIxZGm'))  # 좋아요 요소 기다림
        )

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        product_info = extract_product_info(soup, product_url)
    
        return product_info

    finally:
        driver.quit()

def fetch_product_info_thread(chromedriver_path, products_num):
    products_info = []  # 상품 정보를 저장할 리스트
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(get_individual_product_info, chromedriver_path, product) for product in products_num]
        for future in futures:
            try:
                product_info = future.result()
                products_info.append(product_info)  # 결과를 리스트에 추가
            except Exception as e:
                print(f"Error fetching product info: {e}")
    return products_info

def fetch_product_info_multiprocess(products_num, chromedriver_path):
    # 각 프로세스에 할당할 작업 분배
    num_processes = 3  # 프로세스 수를 3개로 제한
    chunk_size = len(products_num)
    chunks = [products_num[i:i + chunk_size] for i in range(0, len(products_num), chunk_size)]
    
    with Pool(processes=num_processes) as pool:
        product_info_list = pool.starmap(fetch_product_info_thread, [(chromedriver_path, chunk) for chunk in chunks])
    
    # 각 프로세스의 결과를 병합
    merged_product_info = [item for sublist in product_info_list for item in sublist]
    return merged_product_info

def print_product_data(products_info):
    # 결과 출력
    for product_info in products_info:
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
    product_info = fetch_product_info_multiprocess(products_num, chromedriver_path)
    print_product_data(product_info)
    end_time = time.time()
    print(f'총 실행 시간: {end_time - start_time:.2f}초')  # 실행 시간 계산 및 출력

if __name__ == "__main__":
    main()