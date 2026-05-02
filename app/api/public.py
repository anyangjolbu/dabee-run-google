from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.models import Article
from pydantic import BaseModel

router = APIRouter()

class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    press: str | None
    summary: str | None
    tone_label: str | None
    tier: int | None

    class Config:
        from_attributes = True

@router.get("/articles", response_model=List[ArticleResponse])
def get_articles(db: Session = Depends(get_db), limit: int = 50):
    return db.query(Article).order_by(Article.id.desc()).limit(limit).all()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_articles = db.query(Article).count()
    return {"total_articles": total_articles}
