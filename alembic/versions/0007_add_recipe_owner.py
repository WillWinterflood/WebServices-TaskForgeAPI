"""add recipe ownership

Revision ID: 0007_add_recipe_owner
Revises: 0006_add_recipe_macro_fields
Create Date: 2026-03-10 13:10:00
"""

import sqlalchemy as sa

from alembic import op


revision = "0007_add_recipe_owner"
down_revision = "0006_add_recipe_macro_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.add_column(sa.Column("created_by_user_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_recipes_created_by_user_id", ["created_by_user_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_recipes_created_by_user_id_users",
            "users",
            ["created_by_user_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.drop_constraint("fk_recipes_created_by_user_id_users", type_="foreignkey")
        batch_op.drop_index("ix_recipes_created_by_user_id")
        batch_op.drop_column("created_by_user_id")
