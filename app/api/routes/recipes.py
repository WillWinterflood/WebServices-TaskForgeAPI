from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select

from app.db.session import get_db
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate

router = APIRouter(prefix="/recipes", tags=["2. Recipes"])
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


@router.post(
    "",
    response_model=RecipeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom recipe",
    description="Use this to add your own recipe manually with diet, cuisine, and macro values.",
)
def create_recipe(data: RecipeCreate, db=Depends(get_db)):
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
    )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return map_recipe(recipe)


@router.get(
    "",
    response_model=list[RecipeRead],
    summary="List recipes",
    description="Main confirmation endpoint after importing the healthy-diet dataset. If this returns an empty list, the dataset has not been imported into the current database yet.",
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
    response_model=RecipeRead,
    summary="Get a single recipe",
    description="Use this to inspect one recipe in full after listing or searching recipes.",
)
def get_recipe(recipe_id: int, db=Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or recipe.data_source not in ACTIVE_SOURCES:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return map_recipe(recipe)


@router.patch(
    "/{recipe_id}",
    response_model=RecipeRead,
    summary="Update a custom recipe",
    description="Use this to edit a recipe row manually. Imported healthy-diet rows can also be edited, but the importer may overwrite them if re-run with the same source_code.",
)
def update_recipe(recipe_id: int, data: RecipeUpdate, db=Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or recipe.data_source not in ACTIVE_SOURCES:
        raise HTTPException(status_code=404, detail="Recipe not found")

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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recipe",
    description="Use this to remove a recipe row from the database.",
)
def delete_recipe(recipe_id: int, db=Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or recipe.data_source not in ACTIVE_SOURCES:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
