from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select

from app.db.session import get_db
from app.models.recipe import Recipe
from app.schemas.analytics import RecipeMacroResult, RecipeNutritionSummary

router = APIRouter(prefix="/analytics", tags=["analytics"])


def calc_recipe_macros(recipe):
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

    calories_per_serving = round(total_calories / servings, 2)
    protein_per_serving = round(total_protein / servings, 2)
    carbs_per_serving = round(total_carbs / servings, 2)
    fat_per_serving = round(total_fat / servings, 2)

    macro_ratio = classify_macro_ratio(protein_per_serving, carbs_per_serving, fat_per_serving)

    return {
        "recipe_id": recipe.id,
        "recipe_title": recipe.title,
        "servings": servings,
        "total_calories": round(total_calories, 2),
        "total_protein": round(total_protein, 2),
        "total_carbs": round(total_carbs, 2),
        "total_fat": round(total_fat, 2),
        "calories_per_serving": calories_per_serving,
        "protein_per_serving": protein_per_serving,
        "carbs_per_serving": carbs_per_serving,
        "fat_per_serving": fat_per_serving,
        "macro_ratio": macro_ratio,
        "allergen_ingredients": sorted(list(set(allergen_ingredients))),
    }


def classify_macro_ratio(protein, carbs, fat):
    if protein >= 25 and carbs <= 20:
        return "High Protein"
    if carbs <= 20:
        return "Low Carb"
    if fat >= 25:
        return "High Fat"
    return "Balanced"


def macro_result_from_summary(summary):
    return {
        "recipe_id": summary["recipe_id"],
        "recipe_title": summary["recipe_title"],
        "servings": summary["servings"],
        "calories_per_serving": summary["calories_per_serving"],
        "protein_per_serving": summary["protein_per_serving"],
        "carbs_per_serving": summary["carbs_per_serving"],
        "fat_per_serving": summary["fat_per_serving"],
        "macro_ratio": summary["macro_ratio"],
    }


@router.get("/recipes/{recipe_id}/summary", response_model=RecipeNutritionSummary)
def recipe_nutrition_summary(recipe_id: int = Path(ge=1), db=Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return calc_recipe_macros(recipe)


@router.get("/recipes/high-protein", response_model=list[RecipeMacroResult])
def high_protein_recipes(
    min_protein_per_serving: float = Query(default=25.0, ge=0.0),
    max_carbs_per_serving: float = Query(default=30.0, ge=0.0),
    limit: int = Query(default=10, ge=1, le=100),
    db=Depends(get_db),
):
    recipes = db.scalars(select(Recipe).order_by(Recipe.title.asc())).all()

    matched = []
    for recipe in recipes:
        summary = calc_recipe_macros(recipe)
        if (
            summary["protein_per_serving"] >= min_protein_per_serving
            and summary["carbs_per_serving"] <= max_carbs_per_serving
        ):
            matched.append(macro_result_from_summary(summary))

    matched.sort(key=lambda item: item["protein_per_serving"], reverse=True)
    return matched[:limit]


@router.get("/recipes/low-carb", response_model=list[RecipeMacroResult])
def low_carb_recipes(
    max_carbs_per_serving: float = Query(default=20.0, ge=0.0),
    min_protein_per_serving: float = Query(default=0.0, ge=0.0),
    limit: int = Query(default=10, ge=1, le=100),
    db=Depends(get_db),
):
    recipes = db.scalars(select(Recipe).order_by(Recipe.title.asc())).all()

    matched = []
    for recipe in recipes:
        summary = calc_recipe_macros(recipe)
        if (
            summary["carbs_per_serving"] <= max_carbs_per_serving
            and summary["protein_per_serving"] >= min_protein_per_serving
        ):
            matched.append(macro_result_from_summary(summary))

    matched.sort(key=lambda item: item["carbs_per_serving"])
    return matched[:limit]
