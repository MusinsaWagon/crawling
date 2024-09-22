#!/bin/bash

# 로그 파일 경로 설정
CRON_LOG_FILE="/app/musinsa-pricewagon/log/cron.log"
CRAWLING_LOG_FILE="/app/musinsa-pricewagon/log/error_log.log"

# 로그 파일이 없으면 생성
if [ ! -f "$CRON_LOG_FILE" ]; then
  mkdir -p /app/musinsa-pricewagon/log
  touch "$CRON_LOG_FILE"
fi

# 로그 파일이 없으면 생성
if [ ! -f "$CRAWLING_LOG_FILE" ]; then
  mkdir -p /app/musinsa-pricewagon/log
  touch "$CRAWLING_LOG_FILE"
fi

# cronjob 추가 (오전 6시 한국 시간에 실행)
echo "0 6 * * * root python /app/musinsa/product_day_price.py >> /app/musinsa-pricewagon/log/cron.log 2>&1" >> /etc/crontab

# cron 데몬 시작
cron && tail -f "$CRON_LOG_FILE"