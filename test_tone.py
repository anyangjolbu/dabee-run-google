import sys
import os
sys.path.insert(0, os.getcwd())
import traceback
import google.generativeai as genai
from app.core.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

content = "SK하이닉스 반도체 매출 실적 최고치 달성"
try:
    model = genai.GenerativeModel('gemini-flash-lite-latest', generation_config={"response_mime_type": "application/json"})
    prompt = f"""
    다음 뉴스 기사가 'SK하이닉스' 또는 '반도체 산업'의 관점에서 우호적인지, 비우호적인지, 아니면 중립적인지 분석하세요.
    다음 JSON 형식으로만 정확히 답변하세요:
    {{"tone_label": "우호" 또는 "비우호" 또는 "중립", "tone_reason": "판단한 이유를 1~2문장으로 설명"}}
    
    기사 본문:
    {content}
    """
    response = model.generate_content(prompt)
    print("Response text:", response.text)
except Exception as e:
    print("Error:", e)
    traceback.print_exc()
