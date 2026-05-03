from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.database import engine, Base
from app.api import public, admin, ws
import os
import asyncio
from app.services.pipeline import run_pipeline

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DABEE Run")

# Ensure static and templates dirs exist
os.makedirs("app/web/static", exist_ok=True)
os.makedirs("app/web/templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/web/templates")

# Include routers
app.include_router(public.router, prefix="/api", tags=["public"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(ws.router, tags=["websocket"])

async def periodic_pipeline_task():
    while True:
        try:
            print("Running scheduled pipeline (every 5 mins)...")
            import threading
            threading.Thread(target=run_pipeline).start()
        except Exception as e:
            print(f"Scheduled task error: {e}")
        await asyncio.sleep(300) # 5 minutes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_pipeline_task())
    print("Application started. Database tables checked/created.")
    print("Background scheduler started: 5 min interval")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin")
async def read_admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
