from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def setup_driver(chromedriver_path):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 표시하지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver