import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
from bs4 import BeautifulSoup

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

    img_tag = product.select_one('img')
    img_url = img_tag['src'] if img_tag else 'N/A'

    return {
        'Name': name,
        'Brand': brand,
        'Price': price,
        'Image_URL': img_url
    }

def main():
    # 현재 파일의 디렉토리 경로를 얻음
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # ChromeDriver 경로 설정 (코드 파일과 같은 폴더에 있는 chromedriver)
    chromedriver_path = os.path.join(current_dir, 'chromedriver')

    # Selenium 드라이버 설정
    driver = setup_driver(chromedriver_path)
    
    try:
        driver.get('https://www.musinsa.com/categories/item/003?device=mw&sortCode=1y')

        # 페이지가 로드될 때까지 대기
        time.sleep(5)

        # 동적으로 로드된 HTML 가져오기
        html = driver.page_source

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html, 'lxml')

        # 특정 섹션 내의 특정 클래스명을 가진 div 요소 찾기
        products = soup.select('div.category__sc-rb2kzk-0.irgXw')

        # 인기상품 리스트를 담을 리스트 초기화
        product_list = []

        for product in products:
            product_info = extract_product_info(product)
            product_list.append(product_info)

        # 데이터프레임으로 변환
        df = pd.DataFrame(product_list)

        # 결과 출력
        print(df)

        # 엑셀 파일로 저장
        df.to_excel('musinsa_top_100_products.xlsx', index=False)

    finally:
        # 브라우저 닫기
        driver.quit()

if __name__ == "__main__":
    main()