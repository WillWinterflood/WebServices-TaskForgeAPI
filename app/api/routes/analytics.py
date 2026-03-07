from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.recipe import Recipe
from app.models.user import User
from app.models.user_meal import UserMeal
from app.schemas.analytics import RecipeMacroResult, RecipeNutritionSummary
from app.schemas.meal import UserWeeklyMacros

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


def parse_range(date_from, date_to):
    if date_from and date_to:
        try:
            start = date.fromisoformat(date_from)
            end = date.fromisoformat(date_to)
        except ValueError:
            raise HTTPException(status_code=400, detail="date_from/date_to must be YYYY-MM-DD")

        if start > end:
            raise HTTPException(status_code=400, detail="date_from cannot be after date_to")
        return start, end

    end = date.today()
    start = end - timedelta(days=6)
    return start, end


def weekly_macros_for_user(user_id, start, end, db):
    meals = (
        db.query(UserMeal)
        .filter(UserMeal.user_id == user_id)
        .filter(UserMeal.eaten_on >= start)
        .filter(UserMeal.eaten_on <= end)
        .all()
    )

    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0

    for meal in meals:
        recipe = meal.recipe
        if not recipe:
            continue

        summary = calc_recipe_macros(recipe)
        factor = meal.servings_eaten

        total_calories += summary["calories_per_serving"] * factor
        total_protein += summary["protein_per_serving"] * factor
        total_carbs += summary["carbs_per_serving"] * factor
        total_fat += summary["fat_per_serving"] * factor

    return {
        "user_id": user_id,
        "date_from": start.isoformat(),
        "date_to": end.isoformat(),
        "total_calories": round(total_calories, 2),
        "total_protein": round(total_protein, 2),
        "total_carbs": round(total_carbs, 2),
        "total_fat": round(total_fat, 2),
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


@router.get("/users/{user_id}/weekly-macros", response_model=UserWeeklyMacros)
def user_weekly_macros(
    user_id: int,
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")

    start, end = parse_range(date_from, date_to)
    return weekly_macros_for_user(user_id, start, end, db)


@router.get("/me/weekly-macros", response_model=UserWeeklyMacros)
def me_weekly_macros(
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    start, end = parse_range(date_from, date_to)
    return weekly_macros_for_user(current_user.id, start, end, db)
