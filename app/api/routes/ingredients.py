from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy import select

from app.db.session import get_db
from app.models.ingredient import Ingredient
from app.schemas.error import ErrorResponse
from app.schemas.ingredient import IngredientCreate, IngredientRead, IngredientUpdate

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

COMMON_ERROR_RESPONSES = {
    422: {"model": ErrorResponse, "description": "Validation failed"},
}


@router.post(
    "",
    response_model=IngredientRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        **COMMON_ERROR_RESPONSES,
        409: {"model": ErrorResponse, "description": "Ingredient already exists"},
    },
)
def create_ingredient(payload: IngredientCreate, db=Depends(get_db)):
    existing = db.scalar(select(Ingredient).where(Ingredient.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="Ingredient already exists")

    ingredient = Ingredient(**payload.model_dump())
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.get("", response_model=list[IngredientRead], responses=COMMON_ERROR_RESPONSES)
def list_ingredients(db=Depends(get_db)):
    ingredients = db.scalars(select(Ingredient).order_by(Ingredient.name.asc())).all()
    return ingredients


@router.get(
    "/{ingredient_id}",
    response_model=IngredientRead,
    responses={
        **COMMON_ERROR_RESPONSES,
        404: {"model": ErrorResponse, "description": "Ingredient not found"},
    },
)
def get_ingredient(ingredient_id: int = Path(ge=1), db=Depends(get_db)):
    ingredient = db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.patch(
    "/{ingredient_id}",
    response_model=IngredientRead,
    responses={
        **COMMON_ERROR_RESPONSES,
        400: {"model": ErrorResponse, "description": "No fields provided for update"},
        404: {"model": ErrorResponse, "description": "Ingredient not found"},
        409: {"model": ErrorResponse, "description": "Ingredient already exists"},
    },
)
def update_ingredient(
    payload: IngredientUpdate,
    ingredient_id: int = Path(ge=1),
    db=Depends(get_db),
):
    ingredient = db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    if "name" in updates:
        existing = db.scalar(select(Ingredient).where(Ingredient.name == updates["name"]))
        if existing and existing.id != ingredient_id:
            raise HTTPException(status_code=409, detail="Ingredient already exists")

    for key, value in updates.items():
        setattr(ingredient, key, value)

    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.delete(
    "/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **COMMON_ERROR_RESPONSES,
        404: {"model": ErrorResponse, "description": "Ingredient not found"},
    },
)
def delete_ingredient(ingredient_id: int = Path(ge=1), db=Depends(get_db)):
    ingredient = db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    db.delete(ingredient)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
