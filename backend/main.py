from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.copilot import router as copilot_router

app = FastAPI(title="VoteFlow AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(copilot_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


static_dir = Path(__file__).resolve().parent / "static"
index_file = static_dir / "index.html"


@app.get("/", include_in_schema=False)
def frontend_index():
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "error": "Frontend build not found in container.",
        "fix": "Redeploy using the project Dockerfile so Next.js is built and copied into backend/static.",
    }


if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
