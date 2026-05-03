import sys
import os
sys.path.insert(0, os.getcwd())
from app.services.crawler import crawl_content
from app.services.summarizer import summarize_article
from app.services.tone_analyzer import analyze_tone
from app.services.naver_api import fetch_news

items = fetch_news("SK하이닉스", 1)
if items:
    url = items[0]['link']
    print("Testing URL:", url)
    content = crawl_content(url)
    print("Content length:", len(content))
    if len(content) > 50:
        print("Content sample:", content[:100])
        print("Summary:", summarize_article(content))
        print("Tone:", analyze_tone(content))
    else:
        print("Content too short.")
else:
    print("No items found.")
