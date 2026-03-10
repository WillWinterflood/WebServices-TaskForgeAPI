import re
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select

from app.db.session import get_db
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeMatchRead, RecipeRead

router = APIRouter(prefix="/recipes", tags=["4. Recipe Discovery (Public)"])
ACTIVE_SOURCES = ["healthy_diet_kaggle", "manual"]
TITLE_STOPWORDS = {
    "and",
    "best",
    "clean",
    "comfort",
    "creamy",
    "dairy",
    "delicious",
    "dish",
    "easy",
    "eating",
    "food",
    "free",
    "fresh",
    "gluten",
    "healthy",
    "high",
    "homemade",
    "how",
    "keto",
    "low",
    "made",
    "meal",
    "minute",
    "minutes",
    "paleo",
    "quick",
    "recipe",
    "recipes",
    "simple",
    "style",
    "the",
    "vegan",
    "with",
    "without",
}


class SearchMode(str, Enum):
    recipe = "recipe"
    macros = "macros"


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


def active_recipe_statement():
    return select(Recipe).where(Recipe.data_source.in_(ACTIVE_SOURCES))


def apply_macro_filters(statement, min_protein, max_protein, min_carbs, max_carbs, min_fat, max_fat):
    if min_protein is not None:
        statement = statement.where(Recipe.protein_g >= min_protein)
    if max_protein is not None:
        statement = statement.where(Recipe.protein_g <= max_protein)
    if min_carbs is not None:
        statement = statement.where(Recipe.carbs_g >= min_carbs)
    if max_carbs is not None:
        statement = statement.where(Recipe.carbs_g <= max_carbs)
    if min_fat is not None:
        statement = statement.where(Recipe.fat_g >= min_fat)
    if max_fat is not None:
        statement = statement.where(Recipe.fat_g <= max_fat)
    return statement


def macro_distance(recipe, protein, carbs, fat):
    return round(
        abs(float(recipe.protein_g or 0.0) - protein)
        + abs(float(recipe.carbs_g or 0.0) - carbs)
        + abs(float(recipe.fat_g or 0.0) - fat),
        2,
    )


def signed_macro_distance(actual_value, target_value):
    return round(float(actual_value or 0.0) - float(target_value or 0.0), 2)


def macro_similarity_percent(protein_value, carbs_value, fat_value, target_protein, target_carbs, target_fat):
    distance = round(
        abs(float(protein_value or 0.0) - float(target_protein or 0.0))
        + abs(float(carbs_value or 0.0) - float(target_carbs or 0.0))
        + abs(float(fat_value or 0.0) - float(target_fat or 0.0)),
        2,
    )
    macro_total = max(
        float(target_protein or 0.0) + float(target_carbs or 0.0) + float(target_fat or 0.0),
        1.0,
    )
    return round(max(0.0, 1.0 - (distance / macro_total)) * 100.0, 2)


def normalize_title_token(token):
    word = token.lower().strip()
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def extract_title_terms(title):
    terms = set()
    for token in re.findall(r"[a-zA-Z]+", str(title or "").lower()):
        word = normalize_title_token(token)
        if len(word) < 3:
            continue
        if word in TITLE_STOPWORDS:
            continue
        terms.add(word)
    return terms


def title_overlap_terms(source_recipe, candidate_recipe):
    source_terms = extract_title_terms(source_recipe.title)
    candidate_terms = extract_title_terms(candidate_recipe.title)
    return sorted(source_terms.intersection(candidate_terms))


def similarity_score(shared_terms, source_recipe, candidate_recipe):
    distance = macro_distance(
        candidate_recipe,
        float(source_recipe.protein_g or 0.0),
        float(source_recipe.carbs_g or 0.0),
        float(source_recipe.fat_g or 0.0),
    )
    macro_total = max(
        float(source_recipe.protein_g or 0.0)
        + float(source_recipe.carbs_g or 0.0)
        + float(source_recipe.fat_g or 0.0),
        1.0,
    )
    macro_similarity = max(0.0, 1.0 - (distance / macro_total))

    source_terms = extract_title_terms(source_recipe.title)
    if source_terms:
        title_similarity = len(shared_terms) / len(source_terms)
        return round((title_similarity * 70.0) + (macro_similarity * 30.0), 2)

    return round(macro_similarity * 100.0, 2)


@router.get(
    "/search",
    response_model=list[RecipeRead],
    summary="Search recipes by title, diet, cuisine, and macro ranges",
    description="Public recipe discovery step. Use this to search the healthy recipe dataset by recipe name or macro constraints.",
)
def search_recipes(
    filter_by: SearchMode = Query(
        default=SearchMode.recipe,
        description="Choose the main filter mode: recipe uses title/diet/cuisine, macros uses protein/carbs/fat ranges.",
    ),
    title: str | None = Query(default=None, min_length=1, description="Filter by part of the recipe title."),
    diet_type: str | None = Query(default=None, description="Filter by diet type, for example keto or vegan."),
    cuisine_type: str | None = Query(default=None, description="Filter by cuisine type, for example american or mediterranean."),
    min_protein: float | None = Query(default=None, ge=0.0),
    max_protein: float | None = Query(default=None, ge=0.0),
    min_carbs: float | None = Query(default=None, ge=0.0),
    max_carbs: float | None = Query(default=None, ge=0.0),
    min_fat: float | None = Query(default=None, ge=0.0),
    max_fat: float | None = Query(default=None, ge=0.0),
    sort_by: str = Query(default="title", description="Sort by one of: title, protein_g, carbs_g, fat_g, diet_type, cuisine_type."),
    sort_order: str = Query(default="asc", description="Sort direction: asc or desc."),
    limit: int = Query(default=100, ge=1, le=500),
    db=Depends(get_db),
):
    sort_columns = {
        "title": Recipe.title,
        "protein_g": Recipe.protein_g,
        "carbs_g": Recipe.carbs_g,
        "fat_g": Recipe.fat_g,
        "diet_type": Recipe.diet_type,
        "cuisine_type": Recipe.cuisine_type,
    }

    if sort_by not in sort_columns:
        raise HTTPException(status_code=400, detail="sort_by must be one of: title, protein_g, carbs_g, fat_g, diet_type, cuisine_type")

    if sort_order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="sort_order must be 'asc' or 'desc'")

    statement = active_recipe_statement()

    if filter_by == SearchMode.recipe:
        if title:
            statement = statement.where(Recipe.title.ilike(f"%{title.strip()}%"))

        if diet_type:
            statement = statement.where(Recipe.diet_type == diet_type.strip().lower())

        if cuisine_type:
            statement = statement.where(Recipe.cuisine_type == cuisine_type.strip().lower())

    if filter_by == SearchMode.macros:
        if all(value is None for value in [min_protein, max_protein, min_carbs, max_carbs, min_fat, max_fat]):
            raise HTTPException(status_code=400, detail="Provide at least one macro filter when filter_by is 'macros'")
        statement = apply_macro_filters(statement, min_protein, max_protein, min_carbs, max_carbs, min_fat, max_fat)

    sort_column = sort_columns[sort_by]
    if sort_order == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    recipes = db.scalars(statement.limit(limit)).all()
    return [map_recipe(recipe) for recipe in recipes]


@router.get(
    "/{recipe_id}/similar",
    response_model=list[RecipeMatchRead],
    summary="Find similar recipes by recipe terms or by macros",
    description="Public recipe discovery step. Choose whether similarity should be driven by shared food words in the title or by macro closeness. Recipe mode avoids obviously unrelated results such as chicken recipes matching cakes purely on macros.",
)
def similar_recipes(
    recipe_id: int,
    filter_by: SearchMode = Query(
        default=SearchMode.recipe,
        description="Choose the similarity mode: recipe uses shared food words in recipe titles, macros uses protein/carbs/fat distance.",
    ),
    limit: int = Query(default=5, ge=1, le=25),
    same_diet_only: bool = Query(default=False, description="If true, only compare against recipes with the same diet_type."),
    db=Depends(get_db),
):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or recipe.data_source not in ACTIVE_SOURCES:
        raise HTTPException(status_code=404, detail="Recipe not found")

    candidates = db.scalars(active_recipe_statement().where(Recipe.id != recipe_id)).all()
    if same_diet_only and recipe.diet_type:
        candidates = [item for item in candidates if item.diet_type == recipe.diet_type]

    scored = []
    for candidate in candidates:
        shared_terms = title_overlap_terms(recipe, candidate)
        distance = macro_distance(
            candidate,
            float(recipe.protein_g or 0.0),
            float(recipe.carbs_g or 0.0),
            float(recipe.fat_g or 0.0),
        )
        scored.append(
            {
                **map_recipe(candidate),
                "title_overlap_count": len(shared_terms),
                "shared_title_terms": shared_terms,
                "protein_distance_g": signed_macro_distance(candidate.protein_g, recipe.protein_g),
                "carbs_distance_g": signed_macro_distance(candidate.carbs_g, recipe.carbs_g),
                "fat_distance_g": signed_macro_distance(candidate.fat_g, recipe.fat_g),
                "macro_distance": distance,
                "similarity_score": similarity_score(shared_terms, recipe, candidate),
            }
        )

    if filter_by == SearchMode.recipe:
        overlap_matches = [item for item in scored if item["title_overlap_count"] > 0]
        if overlap_matches:
            scored = overlap_matches
        scored.sort(
            key=lambda item: (
                -item["title_overlap_count"],
                -item["similarity_score"],
                item["macro_distance"],
                item["title"].lower(),
            )
        )
    else:
        scored.sort(
            key=lambda item: (
                item["macro_distance"],
                -item["title_overlap_count"],
                item["title"].lower(),
            )
        )

    return scored[:limit]


@router.get(
    "/recommend",
    response_model=list[RecipeMatchRead],
    summary="Recommend recipes for target macros",
    description="Public recipe discovery step. Returns recipes whose macro profile is closest to the requested protein, carbohydrate, and fat targets.",
)
def recommend_recipes(
    target_protein: float = Query(ge=0.0),
    target_carbs: float = Query(ge=0.0),
    target_fat: float = Query(ge=0.0),
    diet_type: str | None = Query(default=None),
    cuisine_type: str | None = Query(default=None),
    limit: int = Query(default=5, ge=1, le=25),
    db=Depends(get_db),
):
    statement = active_recipe_statement()

    if diet_type:
        statement = statement.where(Recipe.diet_type == diet_type.strip().lower())

    if cuisine_type:
        statement = statement.where(Recipe.cuisine_type == cuisine_type.strip().lower())

    recipes = db.scalars(statement).all()
    scored = []
    for recipe in recipes:
        scored.append(
            {
                **map_recipe(recipe),
                "title_overlap_count": 0,
                "shared_title_terms": [],
                "protein_distance_g": signed_macro_distance(recipe.protein_g, target_protein),
                "carbs_distance_g": signed_macro_distance(recipe.carbs_g, target_carbs),
                "fat_distance_g": signed_macro_distance(recipe.fat_g, target_fat),
                "macro_distance": macro_distance(recipe, target_protein, target_carbs, target_fat),
                "similarity_score": macro_similarity_percent(
                    recipe.protein_g,
                    recipe.carbs_g,
                    recipe.fat_g,
                    target_protein,
                    target_carbs,
                    target_fat,
                ),
            }
        )

    scored.sort(key=lambda item: (item["macro_distance"], item["title"].lower()))
    return scored[:limit]
