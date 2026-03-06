"""create user meals table

Revision ID: 0005_create_user_meals
Revises: 0004_create_users
Create Date: 2026-03-05 17:50:00
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0005_create_user_meals"
down_revision = "0004_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_meals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("servings_eaten", sa.Float(), nullable=False, server_default="1"),
        sa.Column("eaten_on", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_meals_id", "user_meals", ["id"], unique=False)
    op.create_index("ix_user_meals_user_id", "user_meals", ["user_id"], unique=False)
    op.create_index("ix_user_meals_recipe_id", "user_meals", ["recipe_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_meals_recipe_id", table_name="user_meals")
    op.drop_index("ix_user_meals_user_id", table_name="user_meals")
    op.drop_index("ix_user_meals_id", table_name="user_meals")
    op.drop_table("user_meals")
