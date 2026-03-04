from fastapi import APIRouter, Depends, HTTPException, Path

from app.db.session import get_db
from app.models.recipe import Recipe
from app.schemas.analytics import RecipeNutritionSummary
from app.schemas.error import ErrorResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

COMMON_ERROR_RESPONSES = {
    422: {"model": ErrorResponse, "description": "Validation failed"},
}


@router.get(
    "/recipes/{recipe_id}/summary",
    response_model=RecipeNutritionSummary,
    responses={
        **COMMON_ERROR_RESPONSES,
        404: {"model": ErrorResponse, "description": "Recipe not found"},
    },
)
def recipe_nutrition_summary(recipe_id: int = Path(ge=1), db=Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    allergen_ingredients = []

    for link in recipe.recipe_ingredients:
        ingredient = link.ingredient
        if not ingredient:
            continue

        factor = link.quantity_g / 100.0
        total_calories += ingredient.calories_per_100g * factor
        total_protein += ingredient.protein_per_100g * factor
        total_carbs += ingredient.carbs_per_100g * factor
        total_fat += ingredient.fat_per_100g * factor

        if ingredient.is_allergen:
            allergen_ingredients.append(ingredient.name)

    servings = recipe.servings
    if servings < 1:
        servings = 1

    return {
        "recipe_id": recipe.id,
        "recipe_title": recipe.title,
        "servings": servings,
        "total_calories": round(total_calories, 2),
        "total_protein": round(total_protein, 2),
        "total_carbs": round(total_carbs, 2),
        "total_fat": round(total_fat, 2),
        "calories_per_serving": round(total_calories / servings, 2),
        "protein_per_serving": round(total_protein / servings, 2),
        "carbs_per_serving": round(total_carbs / servings, 2),
        "fat_per_serving": round(total_fat / servings, 2),
        "allergen_ingredients": sorted(list(set(allergen_ingredients))),
    }
