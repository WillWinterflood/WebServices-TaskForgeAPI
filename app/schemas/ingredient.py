from pydantic import BaseModel, ConfigDict, Field, field_validator


class IngredientBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    calories_per_100g: float = Field(default=0.0, ge=0.0, le=1000.0)
    protein_per_100g: float = Field(default=0.0, ge=0.0, le=100.0)
    carbs_per_100g: float = Field(default=0.0, ge=0.0, le=100.0)
    fat_per_100g: float = Field(default=0.0, ge=0.0, le=100.0)
    is_allergen: bool = False

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name must not be empty")
        return cleaned


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    calories_per_100g: float | None = Field(default=None, ge=0.0, le=1000.0)
    protein_per_100g: float | None = Field(default=None, ge=0.0, le=100.0)
    carbs_per_100g: float | None = Field(default=None, ge=0.0, le=100.0)
    fat_per_100g: float | None = Field(default=None, ge=0.0, le=100.0)
    is_allergen: bool | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        if value is None:
            return value

        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name must not be empty")
        return cleaned


class IngredientRead(IngredientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
