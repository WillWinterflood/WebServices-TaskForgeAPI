from pydantic import BaseModel


class RecipeNutritionSummary(BaseModel):  # Schema for nutrition of recipe
    recipe_id: int
    recipe_title: str
    servings: int
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    calories_per_serving: float
    protein_per_serving: float
    carbs_per_serving: float
    fat_per_serving: float
    macro_ratio: str
    allergen_ingredients: list[str]


class RecipeMacroResult(BaseModel):
    recipe_id: int
    recipe_title: str
    servings: int
    calories_per_serving: float
    protein_per_serving: float
    carbs_per_serving: float
    fat_per_serving: float
    macro_ratio: str
