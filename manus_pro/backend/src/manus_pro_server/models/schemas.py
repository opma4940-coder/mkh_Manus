from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ApiKeySchema(BaseModel):
    id: str
    name: str
    provider: str
    base_url: str
    key: str
    notes: Optional[str] = None

class TaskCreate(BaseModel):
    goal: str
    token_budget: int = 1000000

class TaskSchema(BaseModel):
    id: str
    status: str
    goal: str
    progress: float
    steps_done: int
    steps_estimate: int
    token_total: int
    created_at: str
    updated_at: str

class ChatRequest(BaseModel):
    message: str
    key_id: Optional[str] = None
    model: Optional[str] = "llama3.1-8b"
    history: List[Dict[str, str]] = []
