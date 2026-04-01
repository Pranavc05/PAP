"""add tutor session and message tables

Revision ID: 0004_add_tutor_sessions_tables
Revises: 0003_add_quiz_engine_tables
Create Date: 2026-04-01 14:35:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0004_add_tutor_sessions_tables"
down_revision = "0003_add_quiz_engine_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tutor_sessions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("lesson_id", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tutor_sessions_user_id"), "tutor_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_tutor_sessions_lesson_id"), "tutor_sessions", ["lesson_id"], unique=False)

    op.create_table(
        "tutor_messages",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("hint_level", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["tutor_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tutor_messages_session_id"), "tutor_messages", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tutor_messages_session_id"), table_name="tutor_messages")
    op.drop_table("tutor_messages")
    op.drop_index(op.f("ix_tutor_sessions_lesson_id"), table_name="tutor_sessions")
    op.drop_index(op.f("ix_tutor_sessions_user_id"), table_name="tutor_sessions")
    op.drop_table("tutor_sessions")
