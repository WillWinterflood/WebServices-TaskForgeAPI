from pydantic import BaseModel


class IngredientCreate(BaseModel):
    name: str
    calories_per_100g: float = 0.0
    protein_per_100g: float = 0.0
    carbs_per_100g: float = 0.0
    fat_per_100g: float = 0.0
    is_allergen: bool = False

    is_vegan: bool | None = None
    is_gluten_free: bool | None = None
    brand: str | None = None
    data_source: str = "manual"
    source_code: str | None = None


class IngredientUpdate(BaseModel):
    name: str | None = None
    calories_per_100g: float | None = None
    protein_per_100g: float | None = None
    carbs_per_100g: float | None = None
    fat_per_100g: float | None = None
    is_allergen: bool | None = None

    is_vegan: bool | None = None
    is_gluten_free: bool | None = None
    brand: str | None = None
    data_source: str | None = None
    source_code: str | None = None


class IngredientRead(BaseModel):
    id: int
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    is_allergen: bool

    is_vegan: bool | None = None
    is_gluten_free: bool | None = None
    brand: str | None = None
    data_source: str
    source_code: str | None = None

    class Config:
        from_attributes = True
