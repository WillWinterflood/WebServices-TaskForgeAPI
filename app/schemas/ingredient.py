from pydantic import BaseModel, Field

class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    calories_per_100g: float = 0.0
    protein_per_100g: float = 0.0
    carbs_per_100g: float = 0.0
    fat_per_100g: float = 0.0
    is_allergen: bool = False

class IngredientRead(BaseModel):
    id: int
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    is_allergen: bool

    class Config:
        from_attributes = True

