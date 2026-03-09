# Healthy Recipe Search and Macro Recommendation API

A FastAPI backend for searching healthy recipes, filtering by macro ranges, and finding similar recipes by macro profile.

## Primary Workflow
1. Start the API
2. Import the healthy-diet dataset
3. Call `GET /api/v1/recipes`
4. Call `GET /api/v1/recipes/search`
5. Call `GET /api/v1/recipes/{recipe_id}/similar`
6. Optionally call `GET /api/v1/recipes/recommend`

If you are unsure where to start in Swagger, open `GET /api/v1/guide` first.

## What The API Does
- list imported healthy recipes
- search recipes by title
- filter recipes by diet type and cuisine type
- filter recipes by protein, carbs, and fat ranges
- find recipes with similar macro profiles
- recommend recipes for target macro values
- optionally create your own manual macro-based recipes

## Quickstart (Local Python)
```bash
py -m pip install -r requirements.txt
py -m alembic -c alembic.ini upgrade head
py -m uvicorn app.main:app --reload
```

Open docs at `http://127.0.0.1:8000/docs`.

## Run with Docker
```bash
docker compose up --build
```

This starts the API on `http://127.0.0.1:8000`.

## Healthy Diet Dataset
Primary dataset:
- Kaggle handle: `thedevastator/healthy-diet-recipes-a-comprehensive-dataset`

Recommended import command:
```bash
py scripts/import_healthy_diet_recipes.py --max-recipes 2000
```

Docker import command:
```bash
docker compose exec api python scripts/import_healthy_diet_recipes.py --max-recipes 2000
```

If `kagglehub` cannot download the dataset on your machine, download the CSV files yourself and use either:
```bash
py scripts/import_healthy_diet_recipes.py --input-dir path\to\dataset-folder --max-recipes 2000
```
or
```bash
py scripts/import_healthy_diet_recipes.py --input-file path\to\All_Diets.csv --max-recipes 2000
```

## Recommended Demo Order
1. `GET /api/v1/guide`
2. `GET /api/v1/recipes`
3. `GET /api/v1/recipes/search?diet_type=keto&min_protein=20`
4. `GET /api/v1/recipes/{recipe_id}/similar`
5. `GET /api/v1/recipes/recommend?target_protein=30&target_carbs=20&target_fat=10`

## Optional Manual CRUD
Use these only after the dataset import is working:
- `POST /api/v1/recipes`
- `PATCH /api/v1/recipes/{recipe_id}`
- `DELETE /api/v1/recipes/{recipe_id}`

## Optional Auth
Auth is kept as an optional extension:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

## API Documentation
- [docs/API_DOC.md](docs/API_DOC.md)

For submission, export `docs/API_DOC.md` to PDF and reference that PDF in the final repo and report.
