"""add project templates and submissions tables

Revision ID: 0005_add_project_system_tables
Revises: 0004_add_tutor_sessions_tables
Create Date: 2026-04-01 16:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0005_add_project_system_tables"
down_revision = "0004_add_tutor_sessions_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_templates",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("difficulty", sa.String(length=32), nullable=False),
        sa.Column("industry", sa.String(length=64), nullable=False),
        sa.Column("problem_statement", sa.Text(), nullable=False),
        sa.Column("business_goal", sa.Text(), nullable=False),
        sa.Column("rubric", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_templates_slug"), "project_templates", ["slug"], unique=True)
    op.create_index(op.f("ix_project_templates_difficulty"), "project_templates", ["difficulty"], unique=False)
    op.create_index(op.f("ix_project_templates_industry"), "project_templates", ["industry"], unique=False)

    op.create_table(
        "project_submissions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("template_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("current_process", sa.Text(), nullable=False),
        sa.Column("proposed_automation", sa.Text(), nullable=False),
        sa.Column("success_metrics", sa.Text(), nullable=False),
        sa.Column("risk_controls", sa.Text(), nullable=False),
        sa.Column("review_feedback", sa.JSON(), nullable=True),
        sa.Column("portfolio_artifacts", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["project_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_submissions_user_id"), "project_submissions", ["user_id"], unique=False)
    op.create_index(op.f("ix_project_submissions_template_id"), "project_submissions", ["template_id"], unique=False)

    project_templates_table = sa.table(
        "project_templates",
        sa.column("id", sa.String),
        sa.column("slug", sa.String),
        sa.column("title", sa.String),
        sa.column("difficulty", sa.String),
        sa.column("industry", sa.String),
        sa.column("problem_statement", sa.Text),
        sa.column("business_goal", sa.Text),
        sa.column("rubric", sa.JSON),
    )

    op.bulk_insert(
        project_templates_table,
        [
            {
                "id": "pt_email_triage_beginner",
                "slug": "email-triage-automation",
                "title": "Automated Email Triage Workflow",
                "difficulty": "Beginner",
                "industry": "Operations",
                "problem_statement": "Support teams manually triage repetitive email requests, causing delays.",
                "business_goal": "Reduce first-response time and route requests accurately.",
                "rubric": [
                    {"key": "process_clarity", "weight": 25},
                    {"key": "automation_fit", "weight": 25},
                    {"key": "risk_controls", "weight": 25},
                    {"key": "kpi_quality", "weight": 25},
                ],
            },
            {
                "id": "pt_onboarding_intermediate",
                "slug": "employee-onboarding-automation",
                "title": "Employee Onboarding Automation",
                "difficulty": "Intermediate",
                "industry": "HR",
                "problem_statement": "Onboarding handoffs across HR, IT, and managers create delays and errors.",
                "business_goal": "Shorten onboarding cycle time and reduce manual follow-ups.",
                "rubric": [
                    {"key": "process_clarity", "weight": 25},
                    {"key": "automation_fit", "weight": 25},
                    {"key": "risk_controls", "weight": 25},
                    {"key": "kpi_quality", "weight": 25},
                ],
            },
            {
                "id": "pt_invoice_ai_advanced",
                "slug": "ai-invoice-processing",
                "title": "AI Invoice Processing Pipeline",
                "difficulty": "Advanced",
                "industry": "Finance",
                "problem_statement": "Invoice approvals rely on manual extraction and validation from varied formats.",
                "business_goal": "Improve throughput and lower error rates with AI-assisted processing and review.",
                "rubric": [
                    {"key": "process_clarity", "weight": 25},
                    {"key": "automation_fit", "weight": 25},
                    {"key": "risk_controls", "weight": 25},
                    {"key": "kpi_quality", "weight": 25},
                ],
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_project_submissions_template_id"), table_name="project_submissions")
    op.drop_index(op.f("ix_project_submissions_user_id"), table_name="project_submissions")
    op.drop_table("project_submissions")
    op.drop_index(op.f("ix_project_templates_industry"), table_name="project_templates")
    op.drop_index(op.f("ix_project_templates_difficulty"), table_name="project_templates")
    op.drop_index(op.f("ix_project_templates_slug"), table_name="project_templates")
    op.drop_table("project_templates")
