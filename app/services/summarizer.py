import google.generativeai as genai
from app.core.config import get_settings

settings = get_settings()

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

def summarize_article(content: str) -> str:
    if not settings.gemini_api_key:
        return "Gemini API 키가 설정되지 않아 요약할 수 없습니다."
        
    if not content or len(content) < 50:
        return "본문이 너무 짧아 요약할 수 없습니다."
        
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"다음 뉴스 기사의 핵심 내용을 3~5문장으로 간결하게 요약해 주세요:\n\n{content}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Summarizer error: {e}")
        return "요약 중 오류가 발생했습니다."
