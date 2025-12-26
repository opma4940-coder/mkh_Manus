from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DispatchRequest(BaseModel):
    task_id: str

@router.post("/agents/dispatch")
def dispatch_agent(body: DispatchRequest):
    # Logic to notify agent_service
    return {"status": "accepted", "task_id": body.task_id}
