from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.recipe import Recipe
from app.models.user_meal import UserMeal
from app.schemas.meal import UserMealCreate, UserMealRead

router = APIRouter(prefix="/meals", tags=["meals"])


def map_meal(meal):
    recipe_title = ""
    if meal.recipe:
        recipe_title = meal.recipe.title

    return {
        "id": meal.id,
        "user_id": meal.user_id,
        "recipe_id": meal.recipe_id,
        "recipe_title": recipe_title,
        "servings_eaten": meal.servings_eaten,
        "eaten_on": meal.eaten_on.isoformat(),
    }


@router.post("", response_model=UserMealRead, status_code=status.HTTP_201_CREATED)
def create_meal(data: UserMealCreate, current_user=Depends(get_current_user), db=Depends(get_db)):
    recipe = db.get(Recipe, data.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if data.servings_eaten <= 0:
        raise HTTPException(status_code=400, detail="servings_eaten must be greater than 0")

    try:
        eaten_on = date.fromisoformat(data.eaten_on)
    except ValueError:
        raise HTTPException(status_code=400, detail="eaten_on must be YYYY-MM-DD")

    meal = UserMeal(
        user_id=current_user.id,
        recipe_id=recipe.id,
        servings_eaten=data.servings_eaten,
        eaten_on=eaten_on,
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return map_meal(meal)


@router.get("/me", response_model=list[UserMealRead])
def list_my_meals(current_user=Depends(get_current_user), db=Depends(get_db)):
    meals = (
        db.query(UserMeal)
        .filter(UserMeal.user_id == current_user.id)
        .order_by(UserMeal.eaten_on.desc(), UserMeal.id.desc())
        .all()
    )
    return [map_meal(meal) for meal in meals]


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: int, current_user=Depends(get_current_user), db=Depends(get_db)):
    meal = db.get(UserMeal, meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    if meal.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed to delete this meal")

    db.delete(meal)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
