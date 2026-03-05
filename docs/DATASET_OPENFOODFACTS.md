# Open Food Facts Dataset Notes

Source link used for this project:
- https://world.openfoodfacts.org/data

Practical export used by import script:
- https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz

## Why this dataset is good for this coursework
- Real-world, large-scale food product data.
- Includes nutrition and allergen metadata that maps naturally to recipe intelligence.
- Supports meaningful analytics beyond CRUD.

## Project usage
- Import script: `scripts/import_openfoodfacts.py`
- Imported rows are stored as ingredients with:
  - `data_source = "openfoodfacts"`
  - optional `source_code` (barcode)
  - nutrition fields per 100g

## Attribution and licensing
Open Food Facts documents licensing and reuse terms on their official data pages.
You should cite Open Food Facts in your report and slides when demonstrating dataset integration.
