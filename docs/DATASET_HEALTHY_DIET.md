# Healthy Diet Dataset Notes

## Dataset
- Kaggle handle: `thedevastator/healthy-diet-recipes-a-comprehensive-dataset`
- Primary combined file: `All_Diets.csv`
- Measured row count in `All_Diets.csv`: `7806`

## Available Files
- `All_Diets.csv`
- `dash.csv`
- `keto.csv`
- `mediterranean.csv`
- `paleo.csv`
- `vegan.csv`

## Main Columns
- `Diet_type`
- `Recipe_name`
- `Cuisine_type`
- `Protein(g)`
- `Carbs(g)`
- `Fat(g)`
- `Extraction_day`
- `Extraction_time`

## Why It Fits The Project
This dataset is strong for a macro-focused recipe API because it directly provides:
- recipe names
- diet categories
- cuisine categories
- macro values

That makes it well suited for:
- macro-based search
- diet filtering
- cuisine filtering
- similar-recipe recommendations based on protein, carbs, and fat

## Tradeoff
This dataset is not ingredient-first. It does not provide a clean ingredient list or substitution graph, so the strongest project story is recipe discovery and macro recommendation rather than ingredient-level analytics.
