from fastapi import APIRouter

router = APIRouter(tags=["1. Start Here"])


@router.get(
    "/health",
    summary="Check API health",
    description="Use this first to confirm the API is running before testing dataset import or recipe search.",
)
def health_check():
    return {"status": "ok"}


@router.get(
    "/guide",
    summary="Show the recommended API workflow",
    description="Use this when you are unsure which endpoint to call first. It explains the intended docs order for the macro-focused recipe API, including the optional authentication path.",
)
def api_guide():
    return {
        "primary_workflow": [
            "1. Run the healthy-diet dataset importer with scripts/import_healthy_diet_recipes.py.",
            "2. If you want protected features, register, log in, and authorize with a bearer token.",
            "3. Use the protected recipe routes to create, update, or delete your own manual recipes.",
            "4. Use GET /api/v1/recipes to confirm imported recipes exist.",
            "5. Use GET /api/v1/recipes/search to filter by title, diet, cuisine, or macro ranges.",
            "6. Use GET /api/v1/recipes/{recipe_id}/similar to find recipes with similar macro profiles.",
            "7. Use GET /api/v1/recipes/meal-plan to build a full plan against target macros.",
            "8. Optionally call GET /api/v1/recipes/recommend with target macros.",
        ],
        "important_notes": [
            "This dataset is strong for macro-based filtering and similarity.",
            "The main API story is recipe search and recommendation, not ingredient-level nutrition.",
            "Read-only recipe discovery endpoints are public.",
            "Creating, updating, and deleting manual recipes requires a bearer token and ownership of that recipe.",
        ],
        "recommended_endpoints": {
            "register_user": "/api/v1/auth/register",
            "log_in": "/api/v1/auth/login",
            "confirm_current_user": "/api/v1/auth/me",
            "create_recipe": "/api/v1/recipes",
            "list_recipes": "/api/v1/recipes",
            "search_recipes": "/api/v1/recipes/search",
            "similar_recipes": "/api/v1/recipes/{recipe_id}/similar",
            "meal_plan": "/api/v1/recipes/meal-plan",
            "recommend_by_macros": "/api/v1/recipes/recommend",
        },
    }
