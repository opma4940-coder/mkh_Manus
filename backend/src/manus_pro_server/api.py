from __future__ import annotations
import uuid
import time
import os
import shutil
import logging
from typing import Any, Dict, List
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import (
    FastAPI, HTTPException, Request, Response,
    APIRouter, Depends, status, UploadFile, File as FastAPIFile
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import db
from .config import (
    FREE_TIER_MODELS,
    # FREE_TIER_QUOTAS, # تم إزالته لأنه غير موجود في config.py
    WORKSPACE_ROOT,
    API_KEY_SLOTS,
    REPO_ROOT,
)
from .models.schemas import TaskCreate
from .workspace_fs import list_dir, read_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    db.init_db()
    yield
    logger.info("Application shutdown")

app = FastAPI(
    title="mkh_Manus Unified API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API V1 Router ---
v1 = APIRouter(prefix="/api/v1")

@v1.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}

@v1.get("/settings/keys")
async def get_settings():
    configured = {}
    for slot in API_KEY_SLOTS:
        val = db.get_setting(slot)
        configured[slot] = bool(val and len(val) > 5)
    
    return {
        "api_keys_configured": configured,
        "models": FREE_TIER_MODELS,
        "quotas": {} # تم استبداله بقيمة فارغة مؤقتاً
    }

@v1.post("/settings/keys")
async def set_keys(req: Dict[str, str]):
    updated = []
    for slot, val in req.items():
        if slot in API_KEY_SLOTS and val:
            db.set_setting(slot, val)
            updated.append(slot)
    return {"ok": True, "updated_slots": updated}

@v1.get("/tasks")
async def list_tasks():
    return db.list_tasks()

@v1.post("/tasks")
async def create_task(req: TaskCreate):
    if not req.goal.strip():
        raise HTTPException(400, "Goal cannot be empty")

    task_id = f"task_{uuid.uuid4().hex[:12]}"
    db.create_task(
        task_id,
        req.goal,
        str(WORKSPACE_ROOT),
        req.token_budget or 1_000_000,
    )
    db.add_event(task_id, "info", "task.queued", "Task created")
    
    task = db.get_task(task_id)
    return {"ok": True, "task_id": task_id, "task": task}

@v1.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@v1.get("/tasks/{task_id}/events")
async def get_events(task_id: str, after: int = 0, limit: int = 500):
    events = db.get_events(task_id, after=after, limit=limit)
    return {"events": events}

@v1.get("/workspace/tree")
async def workspace_tree(path: str = "."):
    return list_dir(path)

@v1.get("/workspace/file")
async def workspace_read_file(path: str):
    return {"content": read_file(path)}

@v1.post("/workspace/upload")
async def upload_file(file: UploadFile = FastAPIFile(...)):
    try:
        upload_dir = WORKSPACE_ROOT / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"ok": True, "path": str(file_path.relative_to(WORKSPACE_ROOT))}
    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(500, str(e))

# Include V1 Router
app.include_router(v1)

# Serve Frontend
frontend_dist = REPO_ROOT / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
