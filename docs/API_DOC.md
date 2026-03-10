# API Doc

## Overview
This project is a FastAPI web service for healthy recipe search and macro-based recommendation.

Main use cases:
- list imported healthy recipes
- search recipes by title
- filter recipes by diet type or cuisine type
- filter recipes by macro ranges
- find similar recipes by recipe words or macro profile
- recommend recipes against target macros
- optionally register, log in, and inspect the current user

## Base URL
- Local: `http://127.0.0.1:8000`
- API prefix: `/api/v1`
- Swagger UI: `/docs`

## How To Run
### Docker
```bash
docker compose up --build
docker compose exec api python scripts/import_healthy_diet_recipes.py --max-recipes 2000
```

### Local Python
```bash
py -m pip install -r requirements.txt
py -m alembic -c alembic.ini upgrade head
py -m uvicorn app.main:app --reload
py scripts/import_healthy_diet_recipes.py --max-recipes 2000
```

## Dataset
This API uses the Kaggle dataset:
- handle: `thedevastator/healthy-diet-recipes-a-comprehensive-dataset`
- main file: `All_Diets.csv`
- measured rows in `All_Diets.csv`: `7806`

Relevant fields from the dataset:
- `Diet_type`
- `Recipe_name`
- `Cuisine_type`
- `Protein(g)`
- `Carbs(g)`
- `Fat(g)`
- `Extraction_day`
- `Extraction_time`

Why this dataset fits:
- strong for macro-based recipe search
- strong for diet and cuisine filtering
- strong for similarity and recommendation based on macros

Tradeoff:
- this is not an ingredient-first dataset
- the strongest project story is recipe discovery and macro recommendation

## Authentication
Authentication is optional in this project.

Protected route:
- `GET /api/v1/auth/me`
- `POST /api/v1/recipes`
- `PATCH /api/v1/recipes/{recipe_id}`
- `DELETE /api/v1/recipes/{recipe_id}`

Bearer token flow:
1. call `POST /api/v1/auth/register`
2. call `POST /api/v1/auth/login`
3. copy `access_token`
4. use Swagger `Authorize`
5. call `GET /api/v1/auth/me`
6. use the same bearer token for recipe create, update, and delete

## Error Format
The API uses a consistent error wrapper.

Example:
```json
{
  "error": {
    "status": 404,
    "code": "not_found",
    "message": "Recipe not found"
  }
}
```

Common codes:
- `400` bad request
- `401` unauthorized
- `403` forbidden
- `404` not found
- `409` conflict
- `422` validation error
- `500` internal server error

## Recommended Demo Order
1. `GET /api/v1/guide`
2. `GET /api/v1/recipes`
3. `GET /api/v1/recipes/search`
4. `GET /api/v1/recipes/{recipe_id}/similar`
5. `GET /api/v1/recipes/recommend`
6. optional auth demo

## Endpoint Reference
### 1. Start Here
#### `GET /api/v1/health`
Purpose:
- confirm the API is running

Success response:
```json
{
  "status": "ok"
}
```

#### `GET /api/v1/guide`
Purpose:
- returns the intended workflow for the API

Success response:
```json
{
  "primary_workflow": [
    "1. Run the healthy-diet dataset importer with scripts/import_healthy_diet_recipes.py.",
    "2. Call GET /api/v1/recipes to confirm imported recipes exist.",
    "3. Call GET /api/v1/recipes/search to filter by title, diet, cuisine, or macro ranges.",
    "4. Call GET /api/v1/recipes/{recipe_id}/similar to find recipes with similar macro profiles.",
    "5. Optionally call GET /api/v1/recipes/recommend with target macros."
  ]
}
```

### 2. Recipes
#### `GET /api/v1/recipes`
Purpose:
- list recipe rows currently stored in the database

Query parameters:
- `limit`: max rows returned
- `source`: optional source filter such as `healthy_diet_kaggle` or `manual`

Example:
```bash
curl "http://127.0.0.1:8000/api/v1/recipes?limit=3"
```

#### `GET /api/v1/recipes/{recipe_id}`
Purpose:
- get one recipe by id

#### `POST /api/v1/recipes`
Purpose:
- create a manual recipe row
- requires a bearer token
- the new recipe is linked to the logged-in user

Request body example:
```json
{
  "title": "Custom High Protein Bowl",
  "description": "Simple manual macro-based recipe example.",
  "servings": 2,
  "diet_type": "high-protein",
  "cuisine_type": "american",
  "protein_g": 32.0,
  "carbs_g": 24.0,
  "fat_g": 12.0
}
```

#### `PATCH /api/v1/recipes/{recipe_id}`
Purpose:
- update a recipe row
- requires a bearer token
- only the user who created that manual recipe can update it
- imported dataset recipes are read-only

Request body example:
```json
{
  "diet_type": "vegan",
  "protein_g": 28.0,
  "carbs_g": 18.0,
  "fat_g": 9.0
}
```

#### `DELETE /api/v1/recipes/{recipe_id}`
Purpose:
- delete a recipe row
- requires a bearer token
- only the user who created that manual recipe can delete it
- imported dataset recipes are read-only

Response:
- `204 No Content`

#### `GET /api/v1/recipes/search`
Purpose:
- search recipes with a toggle between recipe-style filtering and macro filtering

Key query parameters:
- `filter_by`
  - `recipe`
  - `macros`
- `title`
- `diet_type`
- `cuisine_type`
- `min_protein`
- `max_protein`
- `min_carbs`
- `max_carbs`
- `min_fat`
- `max_fat`
- `sort_by`
- `sort_order`
- `limit`

Recipe-mode example:
```bash
curl "http://127.0.0.1:8000/api/v1/recipes/search?filter_by=recipe&title=chicken&limit=5"
```

Macro-mode example:
```bash
curl "http://127.0.0.1:8000/api/v1/recipes/search?filter_by=macros&min_protein=20&max_fat=20&limit=5"
```

#### `GET /api/v1/recipes/{recipe_id}/similar`
Purpose:
- find similar recipes

Similarity toggle:
- `filter_by=recipe`
  - prioritises shared food words in recipe titles
- `filter_by=macros`
  - prioritises macro closeness

Other query parameters:
- `limit`
- `same_diet_only`

Example:
```bash
curl "http://127.0.0.1:8000/api/v1/recipes/798/similar?filter_by=recipe&limit=3"
```

Response fields of interest:
- `shared_title_terms`
- `title_overlap_count`
- `similarity_score`
- `macro_distance`
- `protein_distance_g`
- `carbs_distance_g`
- `fat_distance_g`

Distance interpretation:
- negative value means the compared recipe is below the source recipe
- positive value means the compared recipe is above the source recipe

Example response fragment:
```json
{
  "title": "20-Minute Paleo Cashew Chicken",
  "shared_title_terms": ["cashew", "chicken"],
  "title_overlap_count": 2,
  "similarity_score": 88.15,
  "macro_distance": 308.24,
  "protein_distance_g": 23.73,
  "carbs_distance_g": -214.89,
  "fat_distance_g": -69.62
}
```

#### `GET /api/v1/recipes/recommend`
Purpose:
- recommend recipes close to a target macro profile

Required query parameters:
- `target_protein`
- `target_carbs`
- `target_fat`

Optional query parameters:
- `diet_type`
- `cuisine_type`
- `limit`

Example:
```bash
curl "http://127.0.0.1:8000/api/v1/recipes/recommend?target_protein=30&target_carbs=20&target_fat=10&limit=5"
```

### 3. Auth (Optional)
#### `POST /api/v1/auth/register`
Purpose:
- create a user account

Request body example:
```json
{
  "email": "user@example.com",
  "full_name": "Example User",
  "password": "password123"
}
```

#### `POST /api/v1/auth/login`
Purpose:
- return a bearer token

Request body example:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Success response example:
```json
{
  "access_token": "token-value",
  "token_type": "bearer"
}
```

#### `GET /api/v1/auth/me`
Purpose:
- return the authenticated user

Requires:
- bearer token

## Submission Checklist For This API Doc
- project overview included
- setup and run instructions included
- dataset choice documented
- auth process documented
- endpoint list documented
- parameters documented
- example requests included
- response structure documented
- error format documented

## Final Note
For coursework submission, export this markdown file as a PDF and reference that PDF in `README.md`.
