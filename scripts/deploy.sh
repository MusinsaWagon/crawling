#!/bin/bash

# 시스템 타임존을 한국 시간으로 설정
ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

# cron 설치 및 설정
apt-get update && apt-get install -y cron

pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# 로그 파일 경로 설정
CRON_LOG_FILE="/app/log/cron.log"
CRAWLING_LOG_FILE="/app/log/error_log.log"

# 로그 파일이 없으면 생성
if [ ! -f "$CRON_LOG_FILE" ]; then
  mkdir -p /app/log
  touch "$CRON_LOG_FILE"
fi

# 로그 파일이 없으면 생성
if [ ! -f "$CRAWLING_LOG_FILE" ]; then
  mkdir -p /app/log
  touch "$CRAWLING_LOG_FILE"
fi

# cronjob 추가 (오전 6시 한국 시간에 실행)
# echo "0 6 * * * root python /app/musinsa/product_day_price.py >> /app/log/cron.log 2>&1" >> /etc/crontab
echo "* * * * * root python /app/musinsa/product_day_price.py >> /app/log/cron.log 2>&1" >> /etc/crontab

# cron 데몬 시작
cron && tail -f "$CRON_LOG_FILE"