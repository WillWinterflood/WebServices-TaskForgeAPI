from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.recipe_search import router as recipe_search_router
from app.api.routes.recipes import router as recipes_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(recipe_search_router)
api_router.include_router(recipes_router)
api_router.include_router(auth_router)
