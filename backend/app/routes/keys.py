from fastapi import APIRouter
from typing import List

router = APIRouter()

@router.get("/keys")
def list_keys():
    return [{"id": 1, "name": "Default Key", "masked": "sk-...1234"}]

@router.post("/keys")
def create_key(key: dict):
    return {"status": "created"}

@router.put("/keys/{id}")
def update_key(id: int, key: dict):
    return {"status": "updated"}

@router.delete("/keys/{id}")
def delete_key(id: int):
    return {"status": "deleted"}
