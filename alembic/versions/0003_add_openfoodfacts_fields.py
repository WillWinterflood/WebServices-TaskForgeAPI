"""add openfoodfacts fields to ingredients

Revision ID: 0003_add_openfoodfacts_fields
Revises: 0002_create_recipes
Create Date: 2026-03-05 15:05:00
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0003_add_openfoodfacts_fields"
down_revision = "0002_create_recipes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ingredients", sa.Column("is_vegan", sa.Boolean(), nullable=True))
    op.add_column("ingredients", sa.Column("is_gluten_free", sa.Boolean(), nullable=True))
    op.add_column("ingredients", sa.Column("brand", sa.String(length=120), nullable=True))
    op.add_column(
        "ingredients",
        sa.Column("data_source", sa.String(length=50), nullable=False, server_default="manual"),
    )
    op.add_column("ingredients", sa.Column("source_code", sa.String(length=64), nullable=True))

    op.create_index("ix_ingredients_data_source", "ingredients", ["data_source"], unique=False)
    op.create_index("ix_ingredients_source_code", "ingredients", ["source_code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ingredients_source_code", table_name="ingredients")
    op.drop_index("ix_ingredients_data_source", table_name="ingredients")

    op.drop_column("ingredients", "source_code")
    op.drop_column("ingredients", "data_source")
    op.drop_column("ingredients", "brand")
    op.drop_column("ingredients", "is_gluten_free")
    op.drop_column("ingredients", "is_vegan")
