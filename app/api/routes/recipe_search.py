from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select

from app.db.session import get_db
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.schemas.recipe import RecipeRead

router = APIRouter(prefix="/recipes", tags=["recipes"])


def map_recipe(recipe):  # Maps the recipe to the response model
    items = []
    for link in recipe.recipe_ingredients:
        name = ""
        if link.ingredient:
            name = link.ingredient.name
        items.append(
            {
                "ingredient_id": link.ingredient_id,
                "ingredient_name": name,
                "quantity_g": link.quantity_g,
            }
        )

    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "servings": recipe.servings,
        "ingredients": items,
    }


def matches_dietary(recipe, vegan, gluten_free):
    ingredients = [link.ingredient for link in recipe.recipe_ingredients if link.ingredient]

    if vegan:
        for ingredient in ingredients:
            if ingredient.is_vegan is False:
                return False

    if gluten_free:
        for ingredient in ingredients:
            if ingredient.is_gluten_free is False:
                return False

    return True


@router.get("/search", response_model=list[RecipeRead])
def search_recipes(
    title: str | None = Query(default=None, min_length=1),
    ingredient_id: int | None = Query(default=None, ge=1),
    min_servings: int | None = Query(default=None, ge=1),
    max_servings: int | None = Query(default=None, ge=1),
    vegan: bool | None = Query(default=None),
    gluten_free: bool | None = Query(default=None),
    sort_by: str = Query(default="title"),
    sort_order: str = Query(default="asc"),
    db=Depends(get_db),
):
    if min_servings is not None and max_servings is not None and min_servings > max_servings:
        raise HTTPException(status_code=400, detail="min_servings cannot be greater than max_servings")

    sort_columns = {
        "id": Recipe.id,
        "title": Recipe.title,
        "servings": Recipe.servings,
    }

    if sort_by not in sort_columns:
        raise HTTPException(status_code=400, detail="sort_by must be one of: id, title, servings")

    if sort_order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="sort_order must be 'asc' or 'desc'")

    statement = select(Recipe)

    if title:
        statement = statement.where(Recipe.title.ilike(f"%{title.strip()}%"))

    if ingredient_id is not None:
        statement = statement.where(
            Recipe.id.in_(
                select(RecipeIngredient.recipe_id).where(RecipeIngredient.ingredient_id == ingredient_id)
            )
        )

    if min_servings is not None:
        statement = statement.where(Recipe.servings >= min_servings)

    if max_servings is not None:
        statement = statement.where(Recipe.servings <= max_servings)

    sort_column = sort_columns[sort_by]
    if sort_order == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    recipes = db.scalars(statement).all()

    if vegan is not None or gluten_free is not None:
        require_vegan = bool(vegan)
        require_gluten_free = bool(gluten_free)
        recipes = [
            recipe for recipe in recipes if matches_dietary(recipe, require_vegan, require_gluten_free)
        ]

    return [map_recipe(recipe) for recipe in recipes]
