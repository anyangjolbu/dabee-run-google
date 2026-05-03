from app.core.database import SessionLocal
from app.core.models import Article, Recipient
from .naver_api import fetch_news
from .relevance import filter_relevant
from .deduplicator import is_duplicate
from .crawler import crawl_content
from .summarizer import summarize_article
from .tone_analyzer import analyze_tone
from .telegram_sender import send_message
from app.core.config import get_settings
import datetime
import email.utils
import html

settings = get_settings()

def run_pipeline():
    print("Starting actual pipeline run...")
    db = SessionLocal()
    try:
        keywords = [k.strip() for k in settings.search_keywords.split(",") if k.strip()]
        for keyword in keywords:
            print(f"Fetching news for keyword: {keyword}")
            raw_articles = fetch_news(keyword)
            
            for item in raw_articles:
                url = item.get("link", "")
            
            # 네이버 API는 HTML 태그를 포함해서 반환하므로 제거
            title = html.unescape(item.get("title", "").replace("<b>", "").replace("</b>", ""))
            
            # 2. Check Duplicates
            if not url or is_duplicate(db, url):
                continue
                
            # 3. Relevance
            if not filter_relevant(item):
                continue
                
            print(f"Processing new article: {title}")
            
            # 4. Crawl 
            content = crawl_content(url)
            
            # 5. Tone Analysis
            tone_label, tone_reason = analyze_tone(content)
            
            # 6. Summarize
            summary = summarize_article(content)
            
            # Parse Date
            pub_date = None
            if item.get("pubDate"):
                try:
                    pub_date = email.utils.parsedate_to_datetime(item.get("pubDate"))
                except:
                    pass
            
            # 티어 결정 (임시 로직: 비우호면 1, 나머진 2)
            tier = 1 if tone_label == "비우호" else 2
            
            # 7. Save to DB
            new_article = Article(
                url=url,
                title=title,
                content=content,
                summary=summary,
                press="네이버 뉴스", 
                tone_label=tone_label,
                tone_reason=tone_reason,
                tier=tier,
                published_at=pub_date or datetime.datetime.utcnow()
            )
            db.add(new_article)
            db.commit()
            
            # 8. Send Telegram for Tier 1
            if tier == 1:
                msg = f"🚨 <b>[비우호 기사 감지]</b>\n\n<b>제목:</b> {title}\n<b>요약:</b> {summary}\n<b>판단:</b> {tone_reason}\n\n<a href='{url}'>기사 원문 보기</a>"
                
                # DB에 등록된 수신자들에게 발송
                recipients = db.query(Recipient).filter(Recipient.is_active == True).all()
                for recipient in recipients:
                    if recipient.tier_permission <= tier: # 권한 체크
                        send_message(recipient.telegram_id, msg)
            
    except Exception as e:
        print(f"Pipeline error: {e}")
    finally:
        db.close()
    print("Pipeline run completed.")
