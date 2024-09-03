# Python 이미지를 사용
FROM python:3.11-slim

# 작업 디렉토리를 설정
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# cron과 관련된 패키지를 설치
RUN apt-get update && apt-get install -y cron

RUN chmod +x /app/scripts/deploy.sh

# cronjob 추가 ( 오전 6시 실행)
RUN echo "* * * * * root /app/scripts/deploy.sh >> /app/log/cron.log 2>&1" >> /etc/crontab

# cron 데몬과 함께 컨테이너를 실행 (JSON 형식으로 CMD 변경)
CMD ["cron", "-f"]