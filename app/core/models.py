from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    press = Column(String, nullable=True)
    tone_label = Column(String, nullable=True) # e.g., "우호", "비우호", "중립"
    tone_reason = Column(Text, nullable=True)
    tier = Column(Integer, default=2) # 1 or 2
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    tier_permission = Column(Integer, default=2) # e.g., 1 means receives all, 2 means only tier 2
    is_active = Column(Boolean, default=True)

class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)

class SendLog(Base):
    __tablename__ = "send_log"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    recipient_id = Column(Integer, ForeignKey("recipients.id"))
    sent_at = Column(DateTime, server_default=func.now())
    status = Column(String, nullable=False) # e.g., "SUCCESS", "FAILED"
    
    article = relationship("Article")
    recipient = relationship("Recipient")

class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(String, nullable=False, index=True) # YYYY-MM-DD
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, server_default=func.now())
