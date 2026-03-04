from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Ingredient(Base): #Ingredients in the db
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, index=True, nullable=False)
    calories_per_100g = Column(Float, nullable=False, default=0.0)
    protein_per_100g = Column(Float, nullable=False, default=0.0)
    carbs_per_100g = Column(Float, nullable=False, default=0.0)
    fat_per_100g = Column(Float, nullable=False, default=0.0)
    is_allergen = Column(Boolean, nullable=False, default=False)
    recipe_links = relationship("RecipeIngredient", back_populates="ingredient")
