from pydantic import BaseModel

#Ingredient endpoints schemas
class IngredientCreate(BaseModel):
    name: str
    calories_per_100g: float = 0.0
    protein_per_100g: float = 0.0
    carbs_per_100g: float = 0.0
    fat_per_100g: float = 0.0
    is_allergen: bool = False

class IngredientUpdate(BaseModel):
    name: str | None = None
    calories_per_100g: float | None = None
    protein_per_100g: float | None = None
    carbs_per_100g: float | None = None
    fat_per_100g: float | None = None
    is_allergen: bool | None = None

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
