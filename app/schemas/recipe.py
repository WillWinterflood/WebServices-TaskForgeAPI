from pydantic import BaseModel, ConfigDict, Field


class RecipeCreate(BaseModel):
    title: str = Field(description="Recipe title")
    description: str | None = Field(default=None, description="Optional recipe description")
    servings: int | None = Field(default=1, description="How many servings the recipe makes")
    diet_type: str | None = Field(default=None, description="Diet category, for example keto or vegan")
    cuisine_type: str | None = Field(default=None, description="Cuisine category, for example american or mediterranean")
    protein_g: float = Field(default=0.0, ge=0.0, description="Protein grams")
    carbs_g: float = Field(default=0.0, ge=0.0, description="Carbohydrate grams")
    fat_g: float = Field(default=0.0, ge=0.0, description="Fat grams")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Custom High Protein Bowl",
                "description": "Simple manual macro-based recipe example.",
                "servings": 2,
                "diet_type": "high-protein",
                "cuisine_type": "american",
                "protein_g": 32.0,
                "carbs_g": 24.0,
                "fat_g": 12.0,
            }
        }
    )


class RecipeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    servings: int | None = None
    diet_type: str | None = None
    cuisine_type: str | None = None
    protein_g: float | None = Field(default=None, ge=0.0)
    carbs_g: float | None = Field(default=None, ge=0.0)
    fat_g: float | None = Field(default=None, ge=0.0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "diet_type": "vegan",
                "protein_g": 28.0,
                "carbs_g": 18.0,
                "fat_g": 9.0,
            }
        }
    )


class RecipeRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    servings: int
    diet_type: str | None = None
    cuisine_type: str | None = None
    protein_g: float
    carbs_g: float
    fat_g: float
    data_source: str
    source_code: str | None = None
    created_by_user_id: int | None = None

    class Config:
        from_attributes = True


class RecipeMatchRead(RecipeRead):
    similarity_score: float
    title_overlap_count: int
    shared_title_terms: list[str]
    protein_distance_g: float
    carbs_distance_g: float
    fat_distance_g: float
    macro_distance: float


class MealPlanItemRead(BaseModel):
    meal_number: int
    recipe: RecipeRead


class MealPlanRead(BaseModel):
    meals_requested: int
    target_protein_g: float
    target_carbs_g: float
    target_fat_g: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    protein_distance_g: float
    carbs_distance_g: float
    fat_distance_g: float
    total_macro_distance: float
    plan_match_percent: float
    diet_type: str | None = None
    cuisine_type: str | None = None
    recipes: list[MealPlanItemRead]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "meals_requested": 3,
                "target_protein_g": 120.0,
                "target_carbs_g": 150.0,
                "target_fat_g": 45.0,
                "total_protein_g": 116.0,
                "total_carbs_g": 144.0,
                "total_fat_g": 48.0,
                "protein_distance_g": -4.0,
                "carbs_distance_g": -6.0,
                "fat_distance_g": 3.0,
                "total_macro_distance": 13.0,
                "plan_match_percent": 93.78,
                "diet_type": "keto",
                "cuisine_type": None,
                "recipes": [
                    {
                        "meal_number": 1,
                        "recipe": {
                            "id": 101,
                            "title": "Chicken Salad Bowl",
                            "description": "Example recipe",
                            "servings": 1,
                            "diet_type": "keto",
                            "cuisine_type": "american",
                            "protein_g": 38.0,
                            "carbs_g": 22.0,
                            "fat_g": 15.0,
                            "data_source": "healthy_diet_kaggle",
                            "source_code": "healthy_diet:all_diets:101",
                            "created_by_user_id": None,
                        },
                    }
                ],
            }
        }
    )
