import secrets
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import get_db
from app.core.models import AdminSession

settings = get_settings()

def verify_password(password: str) -> bool:
    return secrets.compare_digest(password, settings.admin_password)

def create_session(db: Session) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    db_session = AdminSession(token=token, expires_at=expires_at)
    db.add(db_session)
    db.commit()
    return token

def get_current_admin(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("admin_session")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    db_session = db.query(AdminSession).filter(AdminSession.token == token).first()
    if not db_session or db_session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    
    return True
