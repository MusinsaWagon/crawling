#!/bin/bash

# 기존 컨테이너가 존재하면 삭제
docker rm day-price-container --force || true


# cronjob 추가 (오전 6시 실행)
# echo "0 6 * * * root python /app/main.py >> /app/log/cron.log 2>&1" >> /etc/crontab
echo "* * * * * root python /app/main.py >> /app/log/cron.log 2>&1" >> /etc/crontab

# cron 데몬 시작
cron && tail -f /app/log/cron.log