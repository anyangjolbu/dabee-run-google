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
from app.core.logger import add_log
import datetime
import email.utils
import html

settings = get_settings()

def run_pipeline():
    add_log("▶️ 파이프라인 수집 시작")
    db = SessionLocal()
    try:
        keywords = [k.strip() for k in settings.search_keywords.split(",") if k.strip()]
        for keyword in keywords:
            add_log(f"🔍 '{keyword}' 키워드로 뉴스 검색 중...")
            raw_articles = fetch_news(keyword)
            add_log(f"📥 수집 완료: {len(raw_articles)}건")
            
            processed_count = 0
            for item in raw_articles:
                url = item.get("link", "")
                title = html.unescape(item.get("title", "").replace("<b>", "").replace("</b>", ""))
                
                # 2. Check Duplicates
                if not url or is_duplicate(db, url):
                    continue
                    
                # 3. Relevance
                if not filter_relevant(item):
                    continue
                
                processed_count += 1
                add_log(f"📄 [{processed_count}] {title[:30]}...")
                add_log(f"🔍 크롤링 시작: {url}")
                
                # 4. Crawl 
                content = crawl_content(url)
                add_log(f"✅ 크롤링 완료: {len(content)}자")
                
                # 5. Tone Analysis
                add_log("📊 비우호 감지 시작...")
                tone_label, tone_reason = analyze_tone(content)
                add_log(f"📊 결과: [{tone_label}] {tone_reason[:20]}...")
                
                # 6. Summarize
                add_log("📝 요약 시작...")
                summary = summarize_article(content)
                add_log("✅ 요약 완료")
                
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
                    add_log("📤 텔레그램 전송 시작...")
                    msg = f"🚨 <b>[비우호 기사 감지]</b>\n\n<b>제목:</b> {title}\n<b>요약:</b> {summary}\n<b>판단:</b> {tone_reason}\n\n<a href='{url}'>기사 원문 보기</a>"
                    
                    # DB에 등록된 수신자들에게 발송
                    recipients = db.query(Recipient).filter(Recipient.is_active == True).all()
                    for recipient in recipients:
                        if recipient.tier_permission >= tier: # 권한 체크
                            send_message(recipient.telegram_id, msg)
                    add_log("✅ 텔레그램 전송 완료")
            
            add_log(f"⚙️ '{keyword}' 검색 종료 (신규 처리: {processed_count}건)")
            
    except Exception as e:
        add_log(f"❌ 파이프라인 에러: {e}")
    finally:
        db.close()
    add_log("⏹️ 파이프라인 종료")
