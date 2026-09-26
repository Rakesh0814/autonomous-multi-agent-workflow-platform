from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .memory import memory
from .models import WorkflowRequest, WorkflowResponse
from .workflow import run_workflow

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": settings.gemini_model,
        "crewai_enabled": settings.use_crewai,
        "memory_backend": memory.backend,
        "n8n_enabled": settings.notify_n8n,
    }

@app.post("/api/workflow/run", response_model=WorkflowResponse)
def execute_workflow(payload: WorkflowRequest):
    try:
        return run_workflow(payload.goal)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
