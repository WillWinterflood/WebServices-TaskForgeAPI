from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select

from app.db.session import get_db
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientRead, IngredientUpdate

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
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


@router.get("", response_model=list[IngredientRead])
def list_ingredients(db=Depends(get_db)):
    return db.scalars(select(Ingredient).order_by(Ingredient.name.asc())).all()


@router.get("/{ingredient_id}", response_model=IngredientRead)
def get_ingredient(ingredient_id: int, db=Depends(get_db)):
    ingredient = db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.patch("/{ingredient_id}", response_model=IngredientRead)
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
        source = updates["data_source"]
        if source is None:
            updates["data_source"] = "manual"
        else:
            updates["data_source"] = source.strip().lower() or "manual"

    for field, value in updates.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int, db=Depends(get_db)):
    ingredient = db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    db.delete(ingredient)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
