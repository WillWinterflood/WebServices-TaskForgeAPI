from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers

app = FastAPI(title=settings.app_name)

register_exception_handlers(app)

@app.get("/")
def read_root():
    return {"message": "Recipe Intelligence API running"}


app.include_router(api_router, prefix=settings.api_v1_prefix)
