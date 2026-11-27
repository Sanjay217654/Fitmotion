from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import analytics, auth, users, workouts, analysis, video_analysis
from app.core.config import settings
from app.database.schema_upgrade import ensure_schema_compatibility

app = FastAPI(
    title="FitMotion API",
    description="AI-Powered Sports Performance & Fitness Analytics API.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.backend_cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
settings.upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(workouts.router)
app.include_router(analytics.router)
app.include_router(analysis.router)
app.include_router(video_analysis.router)


@app.on_event("startup")
def apply_local_schema_upgrades() -> None:
    ensure_schema_compatibility()



@app.get("/", tags=["Health"])
def api_root() -> dict[str, str]:
    """Provide a useful landing response while the web client is developed."""
    return {
        "service": "FitMotion API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return application liveness without exposing infrastructure details."""
    return {"status": "ok", "service": "fitmotion-api"}
