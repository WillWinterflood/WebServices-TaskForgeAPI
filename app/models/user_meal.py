from sqlalchemy import Column, Date, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserMeal(Base):
    __tablename__ = "user_meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    servings_eaten = Column(Float, nullable=False, default=1.0)
    eaten_on = Column(Date, nullable=False)

    user = relationship("User", back_populates="meals")
    recipe = relationship("Recipe")
