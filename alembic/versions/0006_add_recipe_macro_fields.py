"""add recipe macro and source fields

Revision ID: 0006_add_recipe_macro_fields
Revises: 0005_create_user_meals
Create Date: 2026-03-09 12:30:00
"""

import sqlalchemy as sa

from alembic import op


revision = "0006_add_recipe_macro_fields"
down_revision = "0005_create_user_meals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_recipes_title", table_name="recipes")
    op.create_index("ix_recipes_title", "recipes", ["title"], unique=False)

    op.add_column("recipes", sa.Column("diet_type", sa.String(length=50), nullable=True))
    op.add_column("recipes", sa.Column("cuisine_type", sa.String(length=80), nullable=True))
    op.add_column("recipes", sa.Column("protein_g", sa.Float(), nullable=False, server_default="0"))
    op.add_column("recipes", sa.Column("carbs_g", sa.Float(), nullable=False, server_default="0"))
    op.add_column("recipes", sa.Column("fat_g", sa.Float(), nullable=False, server_default="0"))
    op.add_column("recipes", sa.Column("data_source", sa.String(length=50), nullable=False, server_default="legacy"))
    op.add_column("recipes", sa.Column("source_code", sa.String(length=64), nullable=True))

    op.create_index("ix_recipes_diet_type", "recipes", ["diet_type"], unique=False)
    op.create_index("ix_recipes_cuisine_type", "recipes", ["cuisine_type"], unique=False)
    op.create_index("ix_recipes_data_source", "recipes", ["data_source"], unique=False)
    op.create_index("ix_recipes_source_code", "recipes", ["source_code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_recipes_source_code", table_name="recipes")
    op.drop_index("ix_recipes_data_source", table_name="recipes")
    op.drop_index("ix_recipes_cuisine_type", table_name="recipes")
    op.drop_index("ix_recipes_diet_type", table_name="recipes")

    op.drop_column("recipes", "source_code")
    op.drop_column("recipes", "data_source")
    op.drop_column("recipes", "fat_g")
    op.drop_column("recipes", "carbs_g")
    op.drop_column("recipes", "protein_g")
    op.drop_column("recipes", "cuisine_type")
    op.drop_column("recipes", "diet_type")

    op.drop_index("ix_recipes_title", table_name="recipes")
    op.create_index("ix_recipes_title", "recipes", ["title"], unique=True)
