from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    payload: dict
    idempotency_key: Optional[str] = None
    workspace_id: Optional[str] = None

@router.post("/tasks")
def create_task(task: TaskCreate):
    # Logic to create task and enqueue agent dispatch
    return {"task_id": "new-task-id", "status": "queued"}

@router.get("/tasks/{id}")
def get_task(id: str):
    return {"id": id, "status": "processing"}

@router.post("/tasks/{id}/replay")
def replay_task(id: str, dry_run: bool = False, overrides: dict = None):
    if dry_run:
        return {"summary": "Dry run summary", "side_effects": "none"}
    return {"status": "replaying"}
