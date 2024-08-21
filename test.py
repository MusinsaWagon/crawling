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
    
    driver = setup_driver(chromedriver_path)
    product_url = f'{MUSINSA_PRODUCT_URL}/{2149254}'
    driver.get(product_url)
    
      # 페이지 로딩 대기
    wait = WebDriverWait(driver, 5)
    
    # 할인된 가격 (sale_price)
    try:
        sale_price_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[1]/div[2]/div[8]/div/div/div/span[2]')))
        sale_price = int(sale_price_element.text.strip().replace(',', '').replace('원', ''))
    except:
        sale_price = 'N/A'
        
    print(sale_price)
        
if __name__ == "__main__":
    main()
