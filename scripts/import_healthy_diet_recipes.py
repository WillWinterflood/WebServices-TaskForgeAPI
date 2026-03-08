import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import kagglehub
except ImportError:
    kagglehub = None

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.recipe import Recipe

DATASET_HANDLE = "thedevastator/healthy-diet-recipes-a-comprehensive-dataset"
CSV_CANDIDATES = ["All_Diets.csv", "vegan.csv", "keto.csv", "mediterranean.csv", "paleo.csv", "dash.csv"]
DATA_SOURCE = "healthy_diet_kaggle"


def normalize_text(value):
    text = str(value or "").strip()
    return text or None


def parse_float(value, default=0.0):
    try:
        text = str(value or "").strip()
        if not text:
            return default
        return max(float(text), 0.0)
    except (TypeError, ValueError):
        return default


def choose_dataset_file(input_file, input_dir):
    if input_file:
        file_path = Path(input_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        return file_path

    if input_dir:
        dataset_dir = Path(input_dir)
    else:
        if kagglehub is None:
            raise RuntimeError("kagglehub is not installed. Install dependencies or pass --input-file.")
        dataset_dir = Path(kagglehub.dataset_download(DATASET_HANDLE))

    for candidate in CSV_CANDIDATES:
        matches = list(dataset_dir.rglob(candidate))
        if matches:
            return matches[0]

    csv_files = list(dataset_dir.rglob("*.csv"))
    if csv_files:
        return csv_files[0]

    raise FileNotFoundError(f"No CSV dataset file found in {dataset_dir}")


def build_description(row):
    parts = []

    diet_type = normalize_text(row.get("Diet_type"))
    if diet_type:
        parts.append(f"Diet type: {diet_type}")

    cuisine_type = normalize_text(row.get("Cuisine_type"))
    if cuisine_type:
        parts.append(f"Cuisine type: {cuisine_type}")

    extraction_day = normalize_text(row.get("Extraction_day"))
    extraction_time = normalize_text(row.get("Extraction_time"))
    if extraction_day or extraction_time:
        timestamp = " ".join(part for part in [extraction_day, extraction_time] if part)
        parts.append(f"Imported from healthy diet dataset on {timestamp}")

    return " | ".join(parts) or None


def import_recipes(dataset_file, max_recipes):
    db = SessionLocal()
    processed = 0
    created = 0
    updated = 0
    skipped = 0
    dataset_stem = dataset_file.stem.lower()

    try:
        with open(dataset_file, "r", encoding="utf-8", errors="ignore", newline="") as handle:
            reader = csv.DictReader(handle)

            for row_index, row in enumerate(reader, start=1):
                if row_index > max_recipes:
                    break

                title = normalize_text(row.get("Recipe_name"))
                if not title:
                    skipped += 1
                    continue

                processed += 1
                source_code = f"healthy_diet:{dataset_stem}:{row_index}"
                recipe = db.scalar(select(Recipe).where(Recipe.source_code == source_code))
                if recipe is None:
                    recipe = Recipe(source_code=source_code)
                    db.add(recipe)
                    created += 1
                else:
                    updated += 1

                recipe.title = title[:160]
                recipe.description = build_description(row)
                recipe.servings = 1
                recipe.diet_type = normalize_text((row.get("Diet_type") or "").lower())
                recipe.cuisine_type = normalize_text((row.get("Cuisine_type") or "").lower())
                recipe.protein_g = parse_float(row.get("Protein(g)"))
                recipe.carbs_g = parse_float(row.get("Carbs(g)"))
                recipe.fat_g = parse_float(row.get("Fat(g)"))
                recipe.data_source = DATA_SOURCE

                if row_index % 250 == 0:
                    db.commit()

        db.commit()
    finally:
        db.close()

    print(f"Dataset file: {dataset_file}")
    print(f"Processed recipes: {processed}")
    print(f"Created recipes: {created}")
    print(f"Updated recipes: {updated}")
    print(f"Skipped rows: {skipped}")


def main():
    parser = argparse.ArgumentParser(description="Import recipes from the healthy diet Kaggle dataset")
    parser.add_argument("--input-file", default=None)
    parser.add_argument("--input-dir", default=None)
    parser.add_argument("--max-recipes", type=int, default=2000)
    args = parser.parse_args()

    dataset_file = choose_dataset_file(args.input_file, args.input_dir)
    import_recipes(dataset_file, args.max_recipes)


if __name__ == "__main__":
    main()
