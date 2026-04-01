from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Process Automation EdTech API",
    version="0.1.0",
    description="MVP API for interactive process automation learning platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str | int]:
    return {"status": "ok", "environment": settings.api_env, "port": settings.api_port}


app.include_router(api_router)
