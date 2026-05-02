from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import verify_password, create_session, get_current_admin
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    password: str

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
    # Run in background to avoid blocking
    threading.Thread(target=run_pipeline).start()
    return {"status": "pipeline_started"}
