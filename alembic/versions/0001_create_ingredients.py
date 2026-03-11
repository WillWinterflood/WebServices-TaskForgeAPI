"""create ingredients table

Revision ID: 0001_create_ingredients
Revises:
Create Date: 2026-03-04 12:45:00
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_create_ingredients"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("calories_per_100g", sa.Float(), nullable=False, server_default="0"),
        sa.Column("protein_per_100g", sa.Float(), nullable=False, server_default="0"),
        sa.Column("carbs_per_100g", sa.Float(), nullable=False, server_default="0"),
        sa.Column("fat_per_100g", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_allergen", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ingredients_id", "ingredients", ["id"])
    op.create_index("ix_ingredients_name", "ingredients", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_ingredients_name", table_name="ingredients")
    op.drop_index("ix_ingredients_id", table_name="ingredients")
    op.drop_table("ingredients")
