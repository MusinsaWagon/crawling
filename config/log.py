import logging
import os
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv()

# 로그 파일 경로 설정
LOG_FILE = os.getenv("LOG_FILE", "application.log")

# 로그 파일이 없으면 생성
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'a').close()
    
# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(f'{LOG_FILE}'), logging.StreamHandler()]
)