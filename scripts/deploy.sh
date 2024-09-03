#!/bin/bash


apt-get update && apt-get install -y cron

pip install --upgrade pip

pip install --no-cache-dir -r requirements.txt

# 로그 파일 경로 설정
LOG_FILE="$HOME/app/log/cron.log"

# 로그 파일이 없으면 생성
if [ ! -f "$LOG_FILE" ]; then
  mkdir -p $HOME/app/log
  touch "$LOG_FILE"
fi

# cronjob 추가 (오전 6시 실행)
# echo "0 6 * * * root python /app/main.py >> /app/log/cron.log 2>&1" >> /etc/crontab

echo "* * * * * root python /app/main.py >> $HOME/app/log/cron.log 2>&1" >> /etc/crontab

# cron 데몬 시작
cron && tail -f "$LOG_FILE"