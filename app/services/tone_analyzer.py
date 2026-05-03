import google.generativeai as genai
import json
from typing import Tuple
from app.core.config import get_settings

settings = get_settings()

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

def analyze_tone(content: str) -> Tuple[str, str]:
    if not settings.gemini_api_key:
        return "중립", "API 키 누락"
        
    if not content or len(content) < 50:
        return "중립", "본문 텍스트 부족"
        
    try:
        model = genai.GenerativeModel('gemini-flash-lite-latest', generation_config={"response_mime_type": "application/json"})
        prompt = f"""
        다음 뉴스 기사가 'SK하이닉스' 또는 '반도체 산업'의 관점에서 우호적인지, 비우호적인지, 아니면 중립적인지 분석하세요.
        다음 JSON 형식으로만 정확히 답변하세요:
        {{"tone_label": "우호" 또는 "비우호" 또는 "중립", "tone_reason": "판단한 이유를 1~2문장으로 설명"}}
        
        기사 본문:
        {content[:3000]}
        """
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        return result.get("tone_label", "중립"), result.get("tone_reason", "분석 실패")
    except Exception as e:
        print(f"Tone Analyzer error: {e}")
        return "중립", "AI 분석 중 오류 발생"
