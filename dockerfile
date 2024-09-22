# Python 이미지를 사용
FROM python:3.11-slim

# 작업 디렉토리를 설정
WORKDIR /app

# 필요한 파일 복사
COPY . .

# 스크립트에 실행 권한 부여
RUN chmod +x /app/scripts/deploy.sh

# 시스템 타임존을 한국 시간으로 설정
RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

# cron 설치 및 설정
RUN apt-get update && apt-get install -y cron

# pip 및 패키지 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 로그를 저장할 외부 경로를 위한 볼륨 설정
VOLUME ["/app/musinsa-pricewagon/log"]

# deploy.sh 스크립트 실행
CMD ["/app/scripts/deploy.sh"]