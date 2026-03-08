from pydantic import BaseModel, ConfigDict, Field, field_validator


def parse_number(value):
    if value is None:
        return value

    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned == "":
            return None
        return float(cleaned)

    return value


class IngredientCreate(BaseModel):
    name: str
    calories_per_100g: float = Field(
        default=0.0,
        description='Use a JSON number like 1 or 1.0. If you want leading zeros, send it as a string like "01".',
        examples=[1, 1.0, "01"],
    )
    protein_per_100g: float = Field(default=0.0, examples=[1, 1.0, "01"])
    carbs_per_100g: float = Field(default=0.0, examples=[1, 1.0, "01"])
    fat_per_100g: float = Field(default=0.0, examples=[1, 1.0, "01"])
    is_allergen: bool = False

    is_vegan: bool | None = None
    is_gluten_free: bool | None = None
    brand: str | None = None
    data_source: str = "manual"
    source_code: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Oats",
                "calories_per_100g": "01",
                "protein_per_100g": "13.2",
                "carbs_per_100g": "67.7",
                "fat_per_100g": "6.5",
                "is_allergen": False,
                "is_vegan": True,
                "is_gluten_free": False,
                "brand": "Example Brand",
                "data_source": "manual",
                "source_code": None,
            }
        }
    )

    @field_validator("calories_per_100g", "protein_per_100g", "carbs_per_100g", "fat_per_100g", mode="before")
    @classmethod
    def parse_numeric_strings(cls, value):
        return parse_number(value)


class IngredientUpdate(BaseModel):
    name: str | None = None
    calories_per_100g: float | None = Field(default=None, examples=[1, 1.0, "01"])
    protein_per_100g: float | None = Field(default=None, examples=[1, 1.0, "01"])
    carbs_per_100g: float | None = Field(default=None, examples=[1, 1.0, "01"])
    fat_per_100g: float | None = Field(default=None, examples=[1, 1.0, "01"])
    is_allergen: bool | None = None

    is_vegan: bool | None = None
    is_gluten_free: bool | None = None
    brand: str | None = None
    data_source: str | None = None
    source_code: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "calories_per_100g": "01",
                "protein_per_100g": "02",
            }
        }
    )

    @field_validator("calories_per_100g", "protein_per_100g", "carbs_per_100g", "fat_per_100g", mode="before")
    @classmethod
    def parse_numeric_strings(cls, value):
        return parse_number(value)


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
