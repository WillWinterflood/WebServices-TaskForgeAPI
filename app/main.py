from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings

app = FastAPI( 
    title=settings.app_name,
    version="0.1.0",
    description="Backend API for recipe management and nutrition analytics.",
)

@app.get("/", tags=["meta"], summary="Root")
def read_root() -> dict[str, str]:
    return {"message": "Recipe Intelligence API running"}

app.include_router(api_router, prefix=settings.api_v1_prefix)

