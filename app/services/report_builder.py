from app.core.database import SessionLocal
from app.core.models import Article, Recipient
from app.services.telegram_sender import send_message
import datetime

def generate_daily_report():
    print("Generating daily report...")
    db = SessionLocal()
    try:
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        articles = db.query(Article).filter(Article.published_at >= yesterday).all()
        
        if not articles:
            print("No articles to report.")
            return
            
        tier1_count = len([a for a in articles if a.tier == 1])
        tier2_count = len([a for a in articles if a.tier == 2])
        
        report_text = f"📊 <b>DABEE Run 일일 뉴스 브리핑</b>\n\n"
        report_text += f"최근 24시간 동안 수집된 기사 현황입니다.\n"
        report_text += f"• 🔴 비우호 (Tier 1): <b>{tier1_count}건</b>\n"
        report_text += f"• 🟢 우호/중립 (Tier 2): <b>{tier2_count}건</b>\n\n"
        
        if tier1_count > 0:
            report_text += "<b>[주요 비우호 기사 목록]</b>\n"
            for a in [a for a in articles if a.tier == 1][:5]: # 상위 5개만
                report_text += f"- <a href='{a.url}'>{a.title}</a>\n"
        elif tier2_count > 0:
            report_text += "<b>[주요 긍정/중립 기사 모아보기]</b>\n"
            for a in [a for a in articles if a.tier == 2][:3]:
                report_text += f"- <a href='{a.url}'>{a.title}</a>\n"
        
        recipients = db.query(Recipient).filter(Recipient.is_active == True).all()
        for rec in recipients:
            send_message(rec.telegram_id, report_text)
            
    except Exception as e:
        print(f"Report generation error: {e}")
    finally:
        db.close()
