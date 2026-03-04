from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.db.session import get_db
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientRead

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("/search", response_model=list[IngredientRead])
def search_foods(
    query: str | None = Query(default=None),
    min_protein: float | None = Query(default=None, ge=0.0),
    max_carbs: float | None = Query(default=None, ge=0.0),
    max_calories: float | None = Query(default=None, ge=0.0),
    source: str | None = Query(default="openfoodfacts"),
    limit: int = Query(default=25, ge=1, le=200),
    db=Depends(get_db),
):
    statement = select(Ingredient)

    if query:
        statement = statement.where(Ingredient.name.ilike(f"%{query.strip()}%"))

    if min_protein is not None:
        statement = statement.where(Ingredient.protein_per_100g >= min_protein)

    if max_carbs is not None:
        statement = statement.where(Ingredient.carbs_per_100g <= max_carbs)

    if max_calories is not None:
        statement = statement.where(Ingredient.calories_per_100g <= max_calories)

    if source:
        statement = statement.where(Ingredient.data_source == source.strip().lower())

    statement = statement.order_by(Ingredient.protein_per_100g.desc()).limit(limit)
    return db.scalars(statement).all()
