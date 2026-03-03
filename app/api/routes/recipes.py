from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select

from app.db.session import get_db
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate

router = APIRouter(prefix="/recipes", tags=["recipes"])


def map_recipe(recipe):
    items = []
    for link in recipe.recipe_ingredients:
        ingredient_name = ""
        if link.ingredient:
            ingredient_name = link.ingredient.name
        items.append(
            {
                "ingredient_id": link.ingredient_id,
                "ingredient_name": ingredient_name,
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


def clean_title(title):
    cleaned = title.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Title is required")
    return cleaned


def clean_servings(servings):
    if servings is None:
        return 1
    if servings < 1:
        raise HTTPException(status_code=400, detail="Servings must be at least 1")
    return servings


def validate_recipe_items(db, ingredients):
    seen = set()
    for item in ingredients:
        if item.ingredient_id in seen:
            raise HTTPException(status_code=400, detail="Duplicate ingredient_id in request")
        seen.add(item.ingredient_id)

        if item.ingredient_id < 1:
            raise HTTPException(status_code=400, detail="ingredient_id must be at least 1")

        if item.quantity_g is None:
            item.quantity_g = 100.0

        if item.quantity_g <= 0:
            raise HTTPException(status_code=400, detail="quantity_g must be greater than 0")

        ingredient = db.get(Ingredient, item.ingredient_id)
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient {item.ingredient_id} not found")


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(data: RecipeCreate, db=Depends(get_db)):
    title = clean_title(data.title)

    existing = db.scalar(select(Recipe).where(Recipe.title == title))
    if existing:
        raise HTTPException(status_code=409, detail="Recipe already exists")

    servings = clean_servings(data.servings)

    ingredients = data.ingredients
    if ingredients is None:
        ingredients = []

    validate_recipe_items(db, ingredients)

    recipe = Recipe(
        title=title,
        description=data.description,
        servings=servings,
    )
    db.add(recipe)
    db.flush()

    for item in ingredients:
        quantity = item.quantity_g
        if quantity is None:
            quantity = 100.0

        db.add(
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=item.ingredient_id,
                quantity_g=quantity,
            )
        )

    db.commit()
    db.refresh(recipe)
    return map_recipe(recipe)


@router.get("", response_model=list[RecipeRead])
def list_recipes(db=Depends(get_db)):
    recipes = db.scalars(select(Recipe).order_by(Recipe.title.asc())).all()
    return [map_recipe(recipe) for recipe in recipes]


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, db=Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return map_recipe(recipe)


@router.patch("/{recipe_id}", response_model=RecipeRead)
def update_recipe(recipe_id: int, data: RecipeUpdate, db=Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    if "title" in updates:
        title = clean_title(data.title)
        existing = db.scalar(select(Recipe).where(Recipe.title == title))
        if existing and existing.id != recipe_id:
            raise HTTPException(status_code=409, detail="Recipe already exists")
        recipe.title = title

    if "description" in updates:
        recipe.description = data.description

    if "servings" in updates:
        if data.servings is None:
            raise HTTPException(status_code=400, detail="Servings cannot be null")
        recipe.servings = clean_servings(data.servings)

    if "ingredients" in updates:
        ingredients = data.ingredients
        if ingredients is None:
            ingredients = []

        validate_recipe_items(db, ingredients)

        recipe.recipe_ingredients.clear()
        for item in ingredients:
            quantity = item.quantity_g
            if quantity is None:
                quantity = 100.0

            recipe.recipe_ingredients.append(
                RecipeIngredient(
                    ingredient_id=item.ingredient_id,
                    quantity_g=quantity,
                )
            )

    db.commit()
    db.refresh(recipe)
    return map_recipe(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, db=Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
