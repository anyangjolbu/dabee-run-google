import requests
from bs4 import BeautifulSoup
import re

def crawl_content(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Naver News specific
        if "news.naver.com" in url:
            article_body = soup.select_one("#dic_area, #articeBody, #newsEndContents")
            if article_body:
                return article_body.get_text(separator="\n", strip=True)
                
        # Generic fallback
        paragraphs = soup.find_all("p")
        content = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
        
        # Clean HTML tags and excessive whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        return content[:5000] # Limit length to avoid blowing up Gemini tokens
    except Exception as e:
        print(f"Crawler error for {url}: {e}")
        return ""
