from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate

router = APIRouter(prefix="/recipes")
ACTIVE_SOURCES = ["healthy_diet_kaggle", "manual"]


def normalize_text(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def map_recipe(recipe):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "servings": recipe.servings,
        "diet_type": recipe.diet_type,
        "cuisine_type": recipe.cuisine_type,
        "protein_g": float(recipe.protein_g or 0.0),
        "carbs_g": float(recipe.carbs_g or 0.0),
        "fat_g": float(recipe.fat_g or 0.0),
        "data_source": recipe.data_source,
        "source_code": recipe.source_code,
        "created_by_user_id": recipe.created_by_user_id,
    }


def clean_title(title):
    cleaned = str(title or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Title is required")
    return cleaned


def clean_servings(servings):
    if servings is None:
        return 1
    if servings < 1:
        raise HTTPException(status_code=400, detail="Servings must be at least 1")
    return servings


def clean_macro(value, field_name):
    if value is None:
        return 0.0
    if value < 0:
        raise HTTPException(status_code=400, detail=f"{field_name} must be zero or greater")
    return float(value)


def ensure_user_can_modify_recipe(recipe, current_user):
    if recipe.data_source != "manual":
        raise HTTPException(status_code=403, detail="Imported recipes are read-only")

    if recipe.created_by_user_id is None or recipe.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only modify your own recipes")


@router.post(
    "",
    tags=["3. Your Recipes (Protected)"],
    response_model=RecipeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom recipe",
    description="Protected recipe action. After registering and logging in, use this to create your own recipe manually with diet, cuisine, and macro values. The recipe will be linked to your account.",
)
def create_recipe(data: RecipeCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    recipe = Recipe(
        title=clean_title(data.title),
        description=normalize_text(data.description),
        servings=clean_servings(data.servings),
        diet_type=normalize_text(data.diet_type.lower()) if data.diet_type else None,
        cuisine_type=normalize_text(data.cuisine_type.lower()) if data.cuisine_type else None,
        protein_g=clean_macro(data.protein_g, "protein_g"),
        carbs_g=clean_macro(data.carbs_g, "carbs_g"),
        fat_g=clean_macro(data.fat_g, "fat_g"),
        data_source="manual",
        source_code=None,
        created_by_user_id=current_user.id,
    )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return map_recipe(recipe)


@router.get(
    "",
    tags=["4. Recipe Discovery (Public)"],
    response_model=list[RecipeRead],
    summary="List recipes",
    description="Public recipe discovery step. Use this after importing the healthy-diet dataset to confirm that recipe rows exist in the current database.",
)
def list_recipes(
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of recipes to return."),
    source: str | None = Query(default=None, description="Optional source filter, for example healthy_diet_kaggle or manual."),
    db=Depends(get_db),
):
    statement = select(Recipe).where(Recipe.data_source.in_(ACTIVE_SOURCES))

    if source:
        statement = statement.where(Recipe.data_source == source.strip().lower())

    recipes = db.scalars(statement.order_by(Recipe.title.asc()).limit(limit)).all()
    return [map_recipe(recipe) for recipe in recipes]


@router.get(
    "/{recipe_id}",
    tags=["4. Recipe Discovery (Public)"],
    response_model=RecipeRead,
    summary="Get a single recipe",
    description="Public recipe discovery step. Use this to inspect one recipe in full after listing or searching recipes.",
)
def get_recipe(recipe_id: int, db=Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or recipe.data_source not in ACTIVE_SOURCES:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return map_recipe(recipe)


@router.patch(
    "/{recipe_id}",
    tags=["3. Your Recipes (Protected)"],
    response_model=RecipeRead,
    summary="Update a custom recipe",
    description="Protected recipe action. Use this to edit one of your own manual recipes. You must be logged in, and only the recipe creator can update it.",
)
def update_recipe(recipe_id: int, data: RecipeUpdate, db=Depends(get_db), current_user=Depends(get_current_user)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or recipe.data_source not in ACTIVE_SOURCES:
        raise HTTPException(status_code=404, detail="Recipe not found")
    ensure_user_can_modify_recipe(recipe, current_user)

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    if "title" in updates:
        recipe.title = clean_title(data.title)

    if "description" in updates:
        recipe.description = normalize_text(data.description)

    if "servings" in updates:
        recipe.servings = clean_servings(data.servings)

    if "diet_type" in updates:
        recipe.diet_type = normalize_text(data.diet_type.lower()) if data.diet_type else None

    if "cuisine_type" in updates:
        recipe.cuisine_type = normalize_text(data.cuisine_type.lower()) if data.cuisine_type else None

    if "protein_g" in updates:
        recipe.protein_g = clean_macro(data.protein_g, "protein_g")

    if "carbs_g" in updates:
        recipe.carbs_g = clean_macro(data.carbs_g, "carbs_g")

    if "fat_g" in updates:
        recipe.fat_g = clean_macro(data.fat_g, "fat_g")

    db.commit()
    db.refresh(recipe)
    return map_recipe(recipe)


@router.delete(
    "/{recipe_id}",
    tags=["3. Your Recipes (Protected)"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recipe",
    description="Protected recipe action. Use this to delete one of your own manual recipes. You must be logged in, and only the recipe creator can delete it.",
)
def delete_recipe(recipe_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or recipe.data_source not in ACTIVE_SOURCES:
        raise HTTPException(status_code=404, detail="Recipe not found")
    ensure_user_can_modify_recipe(recipe, current_user)

    db.delete(recipe)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
