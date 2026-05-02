from sqlalchemy.orm import Session
from app.core.models import Article

def is_duplicate(db: Session, url: str) -> bool:
    return db.query(Article).filter(Article.url == url).first() is not None
