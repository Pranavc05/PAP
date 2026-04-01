"""add quiz engine tables and starter questions

Revision ID: 0003_add_quiz_engine_tables
Revises: 0002_add_learning_tables
Create Date: 2026-04-01 14:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_add_quiz_engine_tables"
down_revision = "0002_add_learning_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("lesson_id", sa.String(length=64), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("correct_option_key", sa.String(length=32), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quiz_questions_lesson_id"), "quiz_questions", ["lesson_id"], unique=False)

    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("lesson_id", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quiz_attempts_lesson_id"), "quiz_attempts", ["lesson_id"], unique=False)
    op.create_index(op.f("ix_quiz_attempts_user_id"), "quiz_attempts", ["user_id"], unique=False)

    quiz_questions_table = sa.table(
        "quiz_questions",
        sa.column("id", sa.String),
        sa.column("lesson_id", sa.String),
        sa.column("prompt", sa.Text),
        sa.column("options", sa.JSON),
        sa.column("correct_option_key", sa.String),
        sa.column("explanation", sa.Text),
        sa.column("position", sa.Integer),
    )

    op.bulk_insert(
        quiz_questions_table,
        [
            {
                "id": "qq_l1_process_1",
                "lesson_id": "lesson_l1_what_is_process",
                "prompt": "Which best describes a business process?",
                "options": [
                    {"key": "a", "text": "A one-time project milestone"},
                    {"key": "b", "text": "A repeatable sequence of steps turning inputs into outputs"},
                    {"key": "c", "text": "Only tasks done by software"},
                    {"key": "d", "text": "An employee job title"},
                ],
                "correct_option_key": "b",
                "explanation": "Processes are repeatable flows with clear inputs, steps, and outputs.",
                "position": 1,
            },
            {
                "id": "qq_l1_automation_1",
                "lesson_id": "lesson_l1_what_is_automation",
                "prompt": "What is the strongest indicator a task should be automated first?",
                "options": [
                    {"key": "a", "text": "The task is repetitive and rules-based"},
                    {"key": "b", "text": "The task is highly strategic and ambiguous"},
                    {"key": "c", "text": "The task happens once a year"},
                    {"key": "d", "text": "The task has no measurable outcome"},
                ],
                "correct_option_key": "a",
                "explanation": "Repetitive, rules-based tasks are top candidates for automation.",
                "position": 1,
            },
            {
                "id": "qq_l1_fit_1",
                "lesson_id": "lesson_l1_automation_criteria",
                "prompt": "Which factor most reduces automation risk?",
                "options": [
                    {"key": "a", "text": "Frequent policy changes and unclear rules"},
                    {"key": "b", "text": "Stable inputs with clear decision criteria"},
                    {"key": "c", "text": "No documentation of current workflow"},
                    {"key": "d", "text": "Only relying on tribal knowledge"},
                ],
                "correct_option_key": "b",
                "explanation": "Stable data and explicit rules make automation more predictable and safer.",
                "position": 1,
            },
            {
                "id": "qq_l1_human_ai_1",
                "lesson_id": "lesson_l1_human_ai_collab",
                "prompt": "Why include human-in-the-loop checks in AI workflows?",
                "options": [
                    {"key": "a", "text": "To increase latency without benefits"},
                    {"key": "b", "text": "To remove all accountability"},
                    {"key": "c", "text": "To review low-confidence outputs and exceptions"},
                    {"key": "d", "text": "To avoid monitoring entirely"},
                ],
                "correct_option_key": "c",
                "explanation": "Humans should review exceptions and uncertain AI decisions.",
                "position": 1,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_quiz_attempts_user_id"), table_name="quiz_attempts")
    op.drop_index(op.f("ix_quiz_attempts_lesson_id"), table_name="quiz_attempts")
    op.drop_table("quiz_attempts")
    op.drop_index(op.f("ix_quiz_questions_lesson_id"), table_name="quiz_questions")
    op.drop_table("quiz_questions")
