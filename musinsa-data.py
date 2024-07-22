import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
from bs4 import BeautifulSoup

# 현재 파일의 디렉토리 경로를 얻음
current_dir = os.path.dirname(os.path.abspath(__file__))

# ChromeDriver 경로 설정 (코드 파일과 같은 폴더에 있는 chromedriver)
chromedriver_path = os.path.join(current_dir, 'chromedriver')

# Selenium을 사용하여 브라우저 열기 (헤드리스 모드)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 브라우저 창을 표시하지 않음
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# ChromeDriver 서비스 설정
service = Service(executable_path=chromedriver_path)

try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://www.musinsa.com/ranking/best')

    # 페이지가 로드될 때까지 대기
    time.sleep(5)

    # 동적으로 로드된 HTML 가져오기
    html = driver.page_source

    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(html, 'lxml')

    # 인기상품 리스트를 담을 리스트 초기화
    product_list = []

    # 상품 정보 추출
    products = soup.select('article[class*="ranking__sc-rg3m2c-0"] ul li')

    for product in products:
        rank = product.select_one('div[class*="ranking__sc-nsn3q8-0"] span').get_text(strip=True)
        name = product.select_one('div[class*="ranking__sc-vvvije-0"] a:nth-of-type(2)').get_text(strip=True)
        brand = product.select_one('div[class*="ranking__sc-vvvije-0"] a:nth-of-type(1)').get_text(strip=True)
        price = product.select_one('div[class*="ranking__sc-gr7nbz-1"] span').get_text(strip=True).replace(',', '').split('원')[0]
        img_url = product.select_one('img')['src']
        
        # 상품 정보를 딕셔너리 형태로 저장
        product_info = {
            'Rank': rank,
            'Name': name,
            'Brand': brand,
            'Price': price,
            'Image_URL': img_url
        }
        
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