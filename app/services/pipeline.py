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

_pipeline_running = False
_pipeline_stop_requested = False

def stop_pipeline():
    global _pipeline_stop_requested
    _pipeline_stop_requested = True
    add_log("🛑 수집 중단 요청됨 (현재 처리 중인 기사가 끝나면 멈춥니다)")

def run_pipeline():
    global _pipeline_running, _pipeline_stop_requested
    if _pipeline_running:
        add_log("⚠️ 파이프라인이 이미 실행 중입니다.")
        return
        
    _pipeline_running = True
    _pipeline_stop_requested = False
    
    add_log("▶️ 파이프라인 수집 시작")
    db = SessionLocal()
    try:
        keywords = [k.strip() for k in settings.search_keywords.split(",") if k.strip()]
        for keyword in keywords:
            if _pipeline_stop_requested:
                break
                
            add_log(f"🔍 '{keyword}' 키워드로 뉴스 검색 중...")
            raw_articles = fetch_news(keyword)
            add_log(f"📥 수집 완료: {len(raw_articles)}건")
            
            processed_count = 0
            for item in raw_articles:
                if _pipeline_stop_requested:
                    add_log("🛑 사용자에 의해 수집이 강제 중단되었습니다.")
                    break
                    
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
                
                # 8. Send Telegram
                msg_tier1 = f"🚨 <b>[비우호 기사 감지]</b>\n\n<b>제목:</b> {title}\n<b>요약:</b> {summary}\n<b>판단:</b> {tone_reason}\n\n<a href='{url}'>기사 원문 보기</a>"
                msg_tier2 = f"📰 <b>[신규 기사 알림 - {tone_label}]</b>\n\n<b>제목:</b> {title}\n<b>요약:</b> {summary}\n\n<a href='{url}'>기사 원문 보기</a>"
                msg = msg_tier1 if tier == 1 else msg_tier2
                
                recipients = db.query(Recipient).filter(Recipient.is_active == True).all()
                sent_count = 0
                for recipient in recipients:
                    if recipient.tier_permission >= tier: # 권한 체크
                        if sent_count == 0:
                            add_log("📤 텔레그램 전송 시작...")
                        send_message(recipient.telegram_id, msg)
                        sent_count += 1
                
                if sent_count > 0:
                    add_log(f"✅ 텔레그램 전송 완료 ({sent_count}명에게 발송)")
            
            add_log(f"⚙️ '{keyword}' 검색 종료 (신규 처리: {processed_count}건)")
            
    except Exception as e:
        add_log(f"❌ 파이프라인 에러: {e}")
    finally:
        _pipeline_running = False
        _pipeline_stop_requested = False
        db.close()
    add_log("⏹️ 파이프라인 종료")
