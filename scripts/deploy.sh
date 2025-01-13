#!/bin/bash

# 시스템 타임존을 한국 시간으로 설정
ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

# cron 설치 및 설정
apt-get update && apt-get install -y cron

pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# 로그 파일 경로 설정
MUSINSA_LOG_FILE="/app/log/musinsa_log.log"

# 로그 파일이 없으면 생성
if [ ! -f "$MUSINSA_LOG_FILE" ]; then
  mkdir -p /app/log
  touch "$MUSINSA_LOG_FILE"
fi

# 환경 변수 파일 로드
export $(grep -v '^#' /app/.env.common | xargs)
export $(grep -v '^#' /app/.env.prod | xargs)

# cronjob 추가 (오전 6시 한국 시간에 실행)
echo "0 6 * * * root ENV=prod python /app/musinsa/product_day_price.py >> /app/log/musinsa_log.log 2>&1" >> /etc/crontab

echo "0 7 * * * root ENV=prod python /app/musinsa/product_register_crawling.py >> /app/log/musinsa_log.log 2>&1" >> /etc/crontab
# cron 데몬 시작
cron && tail -f "$MUSINSA_LOG_FILE"
