"""create recipes and recipe_ingredients tables

Revision ID: 0002_create_recipes
Revises: 0001_create_ingredients
Create Date: 2026-03-04 14:10:00
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_create_recipes"
down_revision = "0001_create_ingredients"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("servings", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recipes_id", "recipes", ["id"])
    op.create_index("ix_recipes_title", "recipes", ["title"], unique=True)

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("quantity_g", sa.Float(), nullable=False, server_default="100"),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipe_ingredient"),
    )
    op.create_index("ix_recipe_ingredients_id", "recipe_ingredients", ["id"])
    op.create_index("ix_recipe_ingredients_recipe_id", "recipe_ingredients", ["recipe_id"])
    op.create_index("ix_recipe_ingredients_ingredient_id", "recipe_ingredients", ["ingredient_id"])


def downgrade() -> None:
    op.drop_index("ix_recipe_ingredients_ingredient_id", table_name="recipe_ingredients")
    op.drop_index("ix_recipe_ingredients_recipe_id", table_name="recipe_ingredients")
    op.drop_index("ix_recipe_ingredients_id", table_name="recipe_ingredients")
    op.drop_table("recipe_ingredients")

    op.drop_index("ix_recipes_title", table_name="recipes")
    op.drop_index("ix_recipes_id", table_name="recipes")
    op.drop_table("recipes")
