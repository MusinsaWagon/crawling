# Python 이미지를 사용
FROM python:3.11-slim

# 작업 디렉토리를 설정
WORKDIR /app

# 필요한 파일 복사
COPY . .

# 스크립트에 실행 권한 부여
RUN chmod +x /app/scripts/deploy.sh

# deploy.sh 스크립트 실행
CMD ["/app/scripts/deploy.sh"]