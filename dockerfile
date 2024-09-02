# Python 이미지를 사용
FROM python:3.11-slim

# 작업 디렉토리를 설정
WORKDIR /app

COPY . .

# cronjob 추가 (매 분마다 실행)
RUN echo "* * * * * root /app/scripts/deploy.sh >> /app/log/cron.log 2>&1" >> /etc/crontab

# cron 데몬과 함께 컨테이너를 실행
CMD cron && tail -f /app/log/cron.log