from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.db.session import get_db
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientRead

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
def create_ingredient(payload: IngredientCreate, db=Depends(get_db)):
    existing = db.scalar(select(Ingredient).where(Ingredient.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="Ingredient already exists")

    ingredient = Ingredient(**payload.model_dump())
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient
