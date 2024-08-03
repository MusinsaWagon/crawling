from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# def setup_driver(chromedriver_path):
#     options = Options()
#     options.add_argument('--headless')  # 브라우저 창을 표시하지 않음
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.page_load_strategy = 'none'  # 페이지 로드 전략 설정

#     service = Service(executable_path=chromedriver_path)
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver

def setup_driver(chromedriver_path):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 표시하지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver