from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.models import Recipient, Article
from app.core.auth import verify_password, create_session, get_current_admin
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    password: str

class RecipientCreate(BaseModel):
    telegram_id: str
    name: str
    tier_permission: int = 2

@router.post("/login")
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    if not verify_password(req.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    token = create_session(db)
    response.set_cookie(key="admin_session", value=token, httponly=True, samesite="lax", max_age=7*24*60*60)
    return {"status": "success"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("admin_session")
    return {"status": "success"}

@router.post("/trigger-pipeline")
def trigger_pipeline(is_admin: bool = Depends(get_current_admin)):
    from app.services.pipeline import run_pipeline
    import threading
    threading.Thread(target=run_pipeline).start()
    return {"status": "pipeline_started"}

@router.post("/stop-pipeline")
def stop_pipeline_api(is_admin: bool = Depends(get_current_admin)):
    from app.services.pipeline import stop_pipeline
    stop_pipeline()
    return {"status": "stopping"}

@router.post("/trigger-report")
def trigger_report(is_admin: bool = Depends(get_current_admin)):
    from app.services.report_builder import generate_daily_report
    import threading
    threading.Thread(target=generate_daily_report).start()
    return {"status": "report_started"}

@router.get("/recipients")
def get_recipients(is_admin: bool = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Recipient).all()

@router.post("/recipients")
def add_recipient(req: RecipientCreate, is_admin: bool = Depends(get_current_admin), db: Session = Depends(get_db)):
    db_recipient = db.query(Recipient).filter(Recipient.telegram_id == req.telegram_id).first()
    if db_recipient:
        raise HTTPException(status_code=400, detail="Already registered")
    new_rec = Recipient(telegram_id=req.telegram_id, name=req.name, tier_permission=req.tier_permission)
    db.add(new_rec)
    db.commit()
    return {"status": "success"}

@router.get("/logs")
def get_logs(is_admin: bool = Depends(get_current_admin), db: Session = Depends(get_db), limit: int = 100):
    return db.query(Article).order_by(Article.id.desc()).limit(limit).all()

@router.get("/live-logs")
def get_live_logs_api(is_admin: bool = Depends(get_current_admin)):
    from app.core.logger import get_live_logs
    return get_live_logs()

@router.delete("/articles")
def reset_articles(is_admin: bool = Depends(get_current_admin), db: Session = Depends(get_db)):
    db.query(Article).delete()
    db.commit()
    return {"status": "success"}

@router.delete("/recipients/{id}")
def delete_recipient(id: int, is_admin: bool = Depends(get_current_admin), db: Session = Depends(get_db)):
    db_recipient = db.query(Recipient).filter(Recipient.id == id).first()
    if not db_recipient:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_recipient)
    db.commit()
    return {"status": "success"}

@router.post("/recipients/{id}/test")
def test_recipient(id: int, is_admin: bool = Depends(get_current_admin), db: Session = Depends(get_db)):
    from app.services.telegram_sender import send_message
    db_recipient = db.query(Recipient).filter(Recipient.id == id).first()
    if not db_recipient:
        raise HTTPException(status_code=404, detail="Not found")
    
    success = send_message(
        db_recipient.telegram_id, 
        f"✅ <b>DABEE Run 연동 테스트</b>\n\n{db_recipient.name}님, 텔레그램 알림 설정이 정상적으로 완료되었습니다!\n(이 메시지가 보인다면 봇이 올바르게 연결된 것입니다.)"
    )
    if not success:
        raise HTTPException(status_code=500, detail="Telegram API Failed")
    return {"status": "success"}
