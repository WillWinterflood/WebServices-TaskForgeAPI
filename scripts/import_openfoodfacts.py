import argparse
import gzip
import io
import json
import sys
from pathlib import Path
from urllib.request import urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.ingredient import Ingredient


DEFAULT_SOURCE_URL = "https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz"


def parse_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def get_nutriment(nutriments, keys, default=0.0):
    for key in keys:
        if key in nutriments:
            return parse_float(nutriments.get(key), default)
    return default


def infer_vegan(labels_tags):
    tags = set(labels_tags or [])
    if "en:vegan" in tags:
        return True
    if "en:non-vegan" in tags:
        return False
    return None


def infer_gluten_free(labels_tags):
    tags = set(labels_tags or [])
    if "en:gluten-free" in tags:
        return True
    if "en:contains-gluten" in tags:
        return False
    return None


def map_product(product):
    name = (product.get("product_name") or "").strip()
    if not name:
        return None

    nutriments = product.get("nutriments") or {}
    labels_tags = product.get("labels_tags") or []

    calories = get_nutriment(nutriments, ["energy-kcal_100g", "energy-kcal_value", "energy-kcal"])
    protein = get_nutriment(nutriments, ["proteins_100g", "proteins"])
    carbs = get_nutriment(nutriments, ["carbohydrates_100g", "carbohydrates"])
    fat = get_nutriment(nutriments, ["fat_100g", "fat"])

    brands = product.get("brands") or ""
    brand = brands.split(",")[0].strip() if brands else None

    record = {
        "name": name[:120],
        "calories_per_100g": max(0.0, calories),
        "protein_per_100g": max(0.0, protein),
        "carbs_per_100g": max(0.0, carbs),
        "fat_per_100g": max(0.0, fat),
        "is_allergen": bool(product.get("allergens_tags")),
        "is_vegan": infer_vegan(labels_tags),
        "is_gluten_free": infer_gluten_free(labels_tags),
        "brand": brand,
        "data_source": "openfoodfacts",
        "source_code": str(product.get("code") or "").strip() or None,
    }

    return record


def iter_products_from_url(url):
    with urlopen(url) as response:
        with gzip.GzipFile(fileobj=response) as gz:
            stream = io.TextIOWrapper(gz, encoding="utf-8", errors="ignore")
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def iter_json_lines(handle):
    for line in handle:
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def iter_products_from_file(path):
    file_path = Path(path)
    if file_path.suffix == ".gz":
        with gzip.open(file_path, "rt", encoding="utf-8", errors="ignore") as handle:
            yield from iter_json_lines(handle)
        return

    with open(file_path, "rt", encoding="utf-8", errors="ignore") as handle:
        yield from iter_json_lines(handle)


def import_openfoodfacts(source_url, input_file, max_products):
    db = SessionLocal()

    processed = 0
    added = 0
    updated = 0
    skipped = 0

    try:
        iterator = iter_products_from_file(input_file) if input_file else iter_products_from_url(source_url)

        for product in iterator:
            if processed >= max_products:
                break

            processed += 1
            mapped = map_product(product)
            if not mapped:
                skipped += 1
                continue

            existing = None
            if mapped["source_code"]:
                existing = db.scalar(
                    select(Ingredient).where(Ingredient.source_code == mapped["source_code"])
                )

            if not existing:
                existing = db.scalar(select(Ingredient).where(Ingredient.name == mapped["name"]))

            if existing:
                if existing.data_source != "openfoodfacts":
                    skipped += 1
                    continue

                existing.calories_per_100g = mapped["calories_per_100g"]
                existing.protein_per_100g = mapped["protein_per_100g"]
                existing.carbs_per_100g = mapped["carbs_per_100g"]
                existing.fat_per_100g = mapped["fat_per_100g"]
                existing.is_allergen = mapped["is_allergen"]
                existing.is_vegan = mapped["is_vegan"]
                existing.is_gluten_free = mapped["is_gluten_free"]
                existing.brand = mapped["brand"]
                existing.source_code = mapped["source_code"]
                updated += 1
            else:
                db.add(Ingredient(**mapped))
                added += 1

            if processed % 200 == 0:
                db.commit()

        db.commit()

    finally:
        db.close()

    print(f"Processed: {processed}")
    print(f"Added: {added}")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")


def main():
    parser = argparse.ArgumentParser(description="Import foods from Open Food Facts JSONL export")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--input-file", default=None)
    parser.add_argument("--max-products", type=int, default=5000)
    args = parser.parse_args()

    import_openfoodfacts(
        source_url=args.source_url,
        input_file=args.input_file,
        max_products=args.max_products,
    )


if __name__ == "__main__":
    main()
