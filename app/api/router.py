from fastapi import APIRouter

from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.foods import router as foods_router
from app.api.routes.health import router as health_router
from app.api.routes.ingredients import router as ingredients_router
from app.api.routes.meals import router as meals_router
from app.api.routes.recipe_search import router as recipe_search_router
from app.api.routes.recipes import router as recipes_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(ingredients_router)
api_router.include_router(recipe_search_router)
api_router.include_router(recipes_router)
api_router.include_router(foods_router)
api_router.include_router(meals_router)
api_router.include_router(analytics_router)
