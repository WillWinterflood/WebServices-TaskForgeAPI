from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.db.session import get_db
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientRead
from app.services.cache import get_cached_json, set_cached_json

router = APIRouter(prefix="/foods", tags=["foods"])


def build_cache_key(query, min_protein, max_carbs, max_calories, source, limit):
    return (
        f"foods:search:q={query or ''}:minp={min_protein}:maxc={max_carbs}:"
        f"maxk={max_calories}:source={source or ''}:limit={limit}"
    )


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
    cache_key = build_cache_key(query, min_protein, max_carbs, max_calories, source, limit)
    cached = get_cached_json(cache_key)
    if cached is not None:
        return cached

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
    rows = db.scalars(statement).all()

    response = [IngredientRead.model_validate(row).model_dump() for row in rows]
    set_cached_json(cache_key, response)
    return response
