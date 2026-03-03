from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Recipe(Base): #Recipes in the db
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    servings = Column(Integer, nullable=False, default=1)

    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
