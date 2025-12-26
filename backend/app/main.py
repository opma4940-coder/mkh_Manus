from fastapi import FastAPI
from app.routes import uploads, tasks, agents, keys

app = FastAPI(title="mkh_Manus API")

app.include_router(uploads.router, tags=["uploads"])
app.include_router(tasks.router, tags=["tasks"])
app.include_router(agents.router, tags=["agents"])
app.include_router(keys.router, tags=["keys"])

@app.get("/")
async def root():
    return {"message": "Welcome to mkh_Manus API"}
