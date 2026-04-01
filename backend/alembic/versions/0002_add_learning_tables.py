"""add learning tables and starter content

Revision ID: 0002_add_learning_tables
Revises: 0001_create_workflows_table
Create Date: 2026-04-01 13:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_add_learning_tables"
down_revision = "0001_create_workflows_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_courses_slug"), "courses", ["slug"], unique=True)
    op.create_index(op.f("ix_courses_level"), "courses", ["level"], unique=False)

    op.create_table(
        "modules",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("course_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_modules_course_id"), "modules", ["course_id"], unique=False)

    op.create_table(
        "lessons",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("module_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lessons_module_id"), "lessons", ["module_id"], unique=False)

    op.create_table(
        "user_lesson_progress",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("lesson_id", sa.String(length=64), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress_user_lesson"),
    )
    op.create_index(op.f("ix_user_lesson_progress_lesson_id"), "user_lesson_progress", ["lesson_id"], unique=False)
    op.create_index(op.f("ix_user_lesson_progress_user_id"), "user_lesson_progress", ["user_id"], unique=False)

    courses_table = sa.table(
        "courses",
        sa.column("id", sa.String),
        sa.column("slug", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("level", sa.Integer),
    )
    modules_table = sa.table(
        "modules",
        sa.column("id", sa.String),
        sa.column("course_id", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("position", sa.Integer),
    )
    lessons_table = sa.table(
        "lessons",
        sa.column("id", sa.String),
        sa.column("module_id", sa.String),
        sa.column("title", sa.String),
        sa.column("objective", sa.Text),
        sa.column("content_markdown", sa.Text),
        sa.column("position", sa.Integer),
    )

    op.bulk_insert(
        courses_table,
        [
            {
                "id": "course_l1_foundations",
                "slug": "foundations-process-automation",
                "title": "Level 1: Foundations of Process Automation",
                "description": "Learn what process automation is, when to use it, and how real business workflows improve.",
                "level": 1,
            }
        ],
    )

    op.bulk_insert(
        modules_table,
        [
            {
                "id": "module_l1_basics",
                "course_id": "course_l1_foundations",
                "title": "Module 1: Process Basics",
                "description": "Understand process structure, repetition, and decision points.",
                "position": 1,
            },
            {
                "id": "module_l1_automation_fit",
                "course_id": "course_l1_foundations",
                "title": "Module 2: Automation Fit",
                "description": "Identify what should and should not be automated using practical criteria.",
                "position": 2,
            },
        ],
    )

    op.bulk_insert(
        lessons_table,
        [
            {
                "id": "lesson_l1_what_is_process",
                "module_id": "module_l1_basics",
                "title": "What is a process?",
                "objective": "Define process inputs, outputs, and handoffs.",
                "content_markdown": "A process is a sequence of repeatable steps that transforms inputs into outputs.",
                "position": 1,
            },
            {
                "id": "lesson_l1_what_is_automation",
                "module_id": "module_l1_basics",
                "title": "What is process automation?",
                "objective": "Explain manual vs automated workflows with examples.",
                "content_markdown": "Automation executes repeatable rules-based tasks with minimal human intervention.",
                "position": 2,
            },
            {
                "id": "lesson_l1_automation_criteria",
                "module_id": "module_l1_automation_fit",
                "title": "What should be automated?",
                "objective": "Apply criteria for selecting automation candidates.",
                "content_markdown": "Good candidates are repetitive, high-volume, rules-based tasks with stable inputs.",
                "position": 1,
            },
            {
                "id": "lesson_l1_human_ai_collab",
                "module_id": "module_l1_automation_fit",
                "title": "Human + AI collaboration",
                "objective": "Design workflows with human-in-the-loop safeguards.",
                "content_markdown": "AI improves speed and triage, while humans handle exceptions and final accountability.",
                "position": 2,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_lesson_progress_user_id"), table_name="user_lesson_progress")
    op.drop_index(op.f("ix_user_lesson_progress_lesson_id"), table_name="user_lesson_progress")
    op.drop_table("user_lesson_progress")
    op.drop_index(op.f("ix_lessons_module_id"), table_name="lessons")
    op.drop_table("lessons")
    op.drop_index(op.f("ix_modules_course_id"), table_name="modules")
    op.drop_table("modules")
    op.drop_index(op.f("ix_courses_level"), table_name="courses")
    op.drop_index(op.f("ix_courses_slug"), table_name="courses")
    op.drop_table("courses")
