"""create documents, extracted_fields

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-09-18

"""

import sqlalchemy as sa

from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source_file", sa.String(), nullable=False),
        sa.Column("content_hash", sa.String(), nullable=False, unique=True),
        sa.Column("full_text", sa.String(), nullable=False),
    )
    op.create_table(
        "extracted_fields",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("document_id", sa.String(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("field_name", sa.String(), nullable=False),
        sa.Column("value", sa.String()),
        sa.Column("evidence_quote", sa.String()),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_table("extracted_fields")
    op.drop_table("documents")
