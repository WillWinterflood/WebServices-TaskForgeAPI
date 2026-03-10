from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), index=True, nullable=False)
    description = Column(Text, nullable=True)
    servings = Column(Integer, nullable=False, default=1)

    diet_type = Column(String(50), nullable=True, index=True)
    cuisine_type = Column(String(80), nullable=True, index=True)
    protein_g = Column(Float, nullable=False, default=0.0)
    carbs_g = Column(Float, nullable=False, default=0.0)
    fat_g = Column(Float, nullable=False, default=0.0)
    data_source = Column(String(50), nullable=False, default="manual", index=True)
    source_code = Column(String(64), nullable=True, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    created_by_user = relationship("User", back_populates="recipes")
