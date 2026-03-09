from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select

from app.db.session import get_db
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientRead, IngredientUpdate

router = APIRouter(prefix="/ingredients", tags=["2. Ingredients"])


@router.post(
    "",
    response_model=IngredientRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom ingredient",
    description="Use this only when you want to add your own ingredient manually. Imported Kaggle ingredients are created automatically by the dataset importer.",
)
def create_ingredient(data: IngredientCreate, db=Depends(get_db)):
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    existing = db.scalar(select(Ingredient).where(Ingredient.name == name))
    if existing:
        raise HTTPException(status_code=409, detail="Ingredient already exists")

    data_source = data.data_source.strip().lower() if data.data_source else "manual"
    if not data_source:
        data_source = "manual"

    ingredient = Ingredient(
        name=name,
        calories_per_100g=data.calories_per_100g,
        protein_per_100g=data.protein_per_100g,
        carbs_per_100g=data.carbs_per_100g,
        fat_per_100g=data.fat_per_100g,
        is_allergen=data.is_allergen,
        is_vegan=data.is_vegan,
        is_gluten_free=data.is_gluten_free,
        brand=data.brand,
        data_source=data_source,
        source_code=data.source_code,
    )

    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.get(
    "",
    response_model=list[IngredientRead],
    summary="List ingredients",
    description="Use this to find ingredient IDs for recipe search or manual recipe creation. The Kaggle import fills this table automatically.",
)
def list_ingredients(
    query: str | None = Query(default=None, description="Filter ingredients by part of the name, for example 'apple' or 'egg'."),
    source: str | None = Query(default=None, description="Filter by source, for example 'kaggle_recipe' or 'manual'."),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of ingredient rows to return."),
    db=Depends(get_db),
):
    statement = select(Ingredient)

    if query:
        statement = statement.where(Ingredient.name.ilike(f"%{query.strip()}%"))

    if source:
        statement = statement.where(Ingredient.data_source == source.strip().lower())

    return db.scalars(statement.order_by(Ingredient.name.asc()).limit(limit)).all()


@router.get(
    "/{ingredient_id}",
    response_model=IngredientRead,
    summary="Get a single ingredient",
    description="Use this when you already know the ingredient ID and want the full stored row.",
)
def get_ingredient(ingredient_id: int, db=Depends(get_db)):
    ingredient = db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.patch(
    "/{ingredient_id}",
    response_model=IngredientRead,
    summary="Update a custom ingredient",
    description="Use this to edit manually maintained ingredient data. This is most useful for adding better nutrition values than the imported dataset provides.",
)
def update_ingredient(ingredient_id: int, data: IngredientUpdate, db=Depends(get_db)):
    ingredient = db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    if "name" in updates:
        name = updates["name"].strip()
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")
        existing = db.scalar(select(Ingredient).where(Ingredient.name == name))
        if existing and existing.id != ingredient_id:
            raise HTTPException(status_code=409, detail="Ingredient already exists")
        updates["name"] = name

    if "data_source" in updates:
        source_value = updates["data_source"]
        if source_value is None:
            updates["data_source"] = "manual"
        else:
            updates["data_source"] = source_value.strip().lower() or "manual"

    for field, value in updates.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.delete(
    "/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an ingredient",
    description="Use this carefully. Deleting an ingredient can affect recipes that reference it.",
)
def delete_ingredient(ingredient_id: int, db=Depends(get_db)):
    ingredient = db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    db.delete(ingredient)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
