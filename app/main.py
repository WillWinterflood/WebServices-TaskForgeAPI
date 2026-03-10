from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers

OPENAPI_TAGS = [
    {
        "name": "1. Start Here",
        "description": "Open this section first. It explains the recommended workflow for importing the healthy recipe dataset and deciding whether you want to stay on the public recipe flow or test protected write features.",
    },
    {
        "name": "2. Authentication Setup",
        "description": "Use this section if you want to register, log in, and authorize with a bearer token before testing protected recipe write actions.",
    },
    {
        "name": "3. Your Recipes (Protected)",
        "description": "These endpoints require a bearer token. Logged-in users can create recipes and can only update or delete recipes that they created themselves.",
    },
    {
        "name": "4. Recipe Discovery (Public)",
        "description": "Public recipe discovery flow. List imported recipes, search by title or macros, inspect one recipe, find similar recipes, and get recommendations.",
    },
]

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description=(
        "Healthy recipe search and macro recommendation API built around a Kaggle healthy diet dataset. "
        "Recommended docs flow: start here, complete authentication if you want protected features, manage your own recipes, then use the public discovery endpoints."
    ),
    openapi_tags=OPENAPI_TAGS,
)

register_exception_handlers(app)


@app.get("/", include_in_schema=False)
def read_root():
    return {
        "message": "Recipe Intelligence API running",
        "docs": "/docs",
        "guide": f"{settings.api_v1_prefix}/guide",
    }


app.include_router(api_router, prefix=settings.api_v1_prefix)
