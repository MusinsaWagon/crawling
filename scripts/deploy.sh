#!/bin/bash

# 기존 컨테이너가 존재하면 삭제
docker rm day-price-container --force || true

python /app/main.py

