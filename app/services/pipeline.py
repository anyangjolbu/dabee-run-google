from app.core.database import SessionLocal
from app.core.models import Article
from .naver_api import fetch_news
from .relevance import filter_relevant
from .deduplicator import is_duplicate
from .crawler import crawl_content
from .summarizer import summarize_article
from .tone_analyzer import analyze_tone
import datetime

def run_pipeline():
    print("Starting pipeline run...")
    db = SessionLocal()
    try:
        # 1. Fetch News
        raw_articles = fetch_news("반도체")
        
        for item in raw_articles:
            url = item["link"]
            title = item["title"]
            
            # 2. Check Duplicates
            if is_duplicate(db, url):
                continue
                
            # 3. Relevance
            if not filter_relevant(item):
                continue
                
            # 4. Crawl (assuming all are Tier 1 for prototype)
            content = crawl_content(url)
            
            # 5. Tone Analysis
            tone_label, tone_reason = analyze_tone(content)
            
            # 6. Summarize
            summary = summarize_article(content)
            
            # 7. Save to DB
            new_article = Article(
                url=url,
                title=title,
                content=content,
                summary=summary,
                press="조선일보", # Stub
                tone_label=tone_label,
                tone_reason=tone_reason,
                tier=1,
                published_at=datetime.datetime.utcnow()
            )
            db.add(new_article)
            db.commit()
            
            print(f"Saved new article: {title}")
            
            # 8. Send Telegram (skip in stub)
            
    finally:
        db.close()
    print("Pipeline run completed.")
