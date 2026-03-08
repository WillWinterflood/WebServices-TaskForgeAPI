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
    description="Use this when you are unsure which endpoint to call first. It explains the intended demo order for the macro-focused recipe API.",
)
def api_guide():
    return {
        "primary_workflow": [
            "1. Run the healthy-diet dataset importer with scripts/import_healthy_diet_recipes.py.",
            "2. Call GET /api/v1/recipes to confirm imported recipes exist.",
            "3. Call GET /api/v1/recipes/search to filter by title, diet, cuisine, or macro ranges.",
            "4. Call GET /api/v1/recipes/{recipe_id}/similar to find recipes with similar macro profiles.",
            "5. Optionally call GET /api/v1/recipes/recommend with target macros.",
        ],
        "important_notes": [
            "This dataset is strong for macro-based filtering and similarity.",
            "The main API story is recipe search and recommendation, not ingredient-level nutrition.",
            "Auth endpoints are optional and are not needed for the main demo.",
        ],
        "recommended_endpoints": {
            "list_recipes": "/api/v1/recipes",
            "search_recipes": "/api/v1/recipes/search",
            "similar_recipes": "/api/v1/recipes/{recipe_id}/similar",
            "recommend_by_macros": "/api/v1/recipes/recommend",
        },
    }
