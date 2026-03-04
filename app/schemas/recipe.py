from pydantic import BaseModel


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity_g: float | None = 100.0


class RecipeIngredientRead(BaseModel):
    ingredient_id: int
    ingredient_name: str
    quantity_g: float


class RecipeCreate(BaseModel):
    title: str
    description: str | None = None
    servings: int | None = 1
    ingredients: list[RecipeIngredientCreate] | None = None


class RecipeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    servings: int | None = None
    ingredients: list[RecipeIngredientCreate] | None = None


class RecipeRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    servings: int
    ingredients: list[RecipeIngredientRead]

    class Config:
        from_attributes = True
