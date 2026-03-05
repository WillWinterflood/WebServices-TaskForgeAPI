# Recipe Intelligence API (COMP3011 Coursework 1)

A FastAPI backend for ingredients, recipes, and nutrition analytics.

## What It Does
- Ingredient CRUD (`/api/v1/ingredients/*`)
- Recipe CRUD with ingredient composition (`/api/v1/recipes/*`)
- Recipe search/filter/sort (`/api/v1/recipes/search`)
- Nutrition analytics (`/api/v1/analytics/*`)
- Food dataset search (`/api/v1/foods/search`)
- Health check (`/api/v1/health`)

## Quickstart
```bash
py -m pip install -r requirements.txt
py -m alembic -c alembic.ini upgrade head
py -m uvicorn app.main:app --reload
```

Open docs at `http://127.0.0.1:8000/docs`.

## Open Food Facts Integration
Dataset source:
- https://world.openfoodfacts.org/data

Importer script:
```bash
py scripts/import_openfoodfacts.py --max-products 2000
```

Optional local file import:
```bash
py scripts/import_openfoodfacts.py --input-file openfoodfacts-products.jsonl.gz --max-products 2000
```

Imported records are marked with:
- `data_source = "openfoodfacts"`
- optional `source_code` barcode

## Example Strong Analytics Endpoints
- `GET /api/v1/analytics/recipes/{recipe_id}/summary`
- `GET /api/v1/analytics/recipes/high-protein?min_protein_per_serving=25`
- `GET /api/v1/analytics/recipes/low-carb?max_carbs_per_serving=20`
- `GET /api/v1/foods/search?min_protein=20&max_carbs=10`

## Assessment Checklist Mapping
- [docs/ASSESSMENT_CHECKLIST.md](docs/ASSESSMENT_CHECKLIST.md)
- [docs/DATASET_OPENFOODFACTS.md](docs/DATASET_OPENFOODFACTS.md)
