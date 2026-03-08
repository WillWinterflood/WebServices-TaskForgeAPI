from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers

OPENAPI_TAGS = [
    {
        "name": "1. Start Here",
        "description": "Open this section first. It explains the recommended workflow for importing the healthy recipe dataset and testing the macro-based endpoints.",
    },
    {
        "name": "2. Recipes",
        "description": "Primary workflow. List recipes, filter by diet/cuisine/macros, inspect one recipe, and find similar recipes by macro profile.",
    },
    {
        "name": "3. Auth (Optional)",
        "description": "Optional extension. Use this only if you want to test authenticated endpoints.",
    },
]

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description=(
        "Healthy recipe search and macro recommendation API built around a Kaggle healthy diet dataset. "
        "Primary workflow: import recipes, list recipes, filter by macros, then find similar recipes."
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
