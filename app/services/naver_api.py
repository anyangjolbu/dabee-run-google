import requests
from app.core.config import get_settings

settings = get_settings()

def fetch_news(query: str, display: int = 20):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": settings.naver_client_id,
        "X-Naver-Client-Secret": settings.naver_client_secret
    }
    params = {
        "query": query,
        "display": display,
        "sort": "date"
    }
    
    if not settings.naver_client_id or not settings.naver_client_secret:
        print("Warning: Naver API keys are missing. Returning empty list.")
        return []

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        print(f"Error fetching news from Naver API: {e}")
        return []
