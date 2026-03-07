from pydantic import BaseModel


class UserMealCreate(BaseModel):
    recipe_id: int
    servings_eaten: float = 1.0
    eaten_on: str


class UserMealRead(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    recipe_title: str
    servings_eaten: float
    eaten_on: str


class UserWeeklyMacros(BaseModel):
    user_id: int
    date_from: str
    date_to: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
