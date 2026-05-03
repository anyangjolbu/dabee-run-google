#!/bin/bash

echo "🚀 DABEE Run 최신 버전 배포를 시작합니다..."

# 1. 최신 코드 가져오기
echo "📦 깃허브에서 코드를 가져옵니다..."
git pull

# 2. 가상환경 활성화 및 패키지 설치
echo "🛠️ 의존성 패키지를 확인/설치합니다..."
source .venv/bin/activate
pip install -r requirements.txt

# 3. 서비스 재시작 (systemd 사용 시)
# sudo systemctl restart dabee

echo "✅ 배포가 완료되었습니다!"
# 임시로 스크립트에서 바로 구동하려면 아래 명령어 사용 (systemd 적용 전)
# pkill -f uvicorn
# nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
# echo "🌐 백그라운드에서 서버가 시작되었습니다. (로그: server.log)"
