import json

from openai import AzureOpenAI

from app.config import get_settings


def _build_azure_client() -> AzureOpenAI | None:
    settings = get_settings()
    if settings.ai_provider.lower().strip() != "azure_openai":
        return None
    required_values = [
        settings.azure_openai_api_key,
        settings.azure_openai_endpoint,
        settings.azure_openai_api_version,
        settings.azure_openai_deployment,
    ]
    if not all(value.strip() for value in required_values):
        return None
    return AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
    )


def generate_project_review(payload: dict) -> dict:
    fallback = {
        "rubric_scores": {
            "process_clarity": 7,
            "automation_fit": 7,
            "risk_controls": 6,
            "kpi_quality": 7,
        },
        "summary": "Good baseline submission with clear intent. Improve risk controls and measurable KPI targets.",
        "improvement_actions": [
            "Map exception flows and escalation paths explicitly.",
            "Define a baseline and target KPI with numeric thresholds.",
            "Add one phased rollout milestone with validation criteria.",
        ],
    }

    settings = get_settings()
    client = _build_azure_client()
    if client is None:
        return fallback

    try:
        completion = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            temperature=0.2,
            max_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert automation project reviewer. "
                        "Return strictly valid JSON with keys: rubric_scores, summary, improvement_actions."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(payload),
                },
            ],
        )
        content = completion.choices[0].message.content or ""
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            return fallback
        return {
            "rubric_scores": parsed.get("rubric_scores", fallback["rubric_scores"]),
            "summary": parsed.get("summary", fallback["summary"]),
            "improvement_actions": parsed.get("improvement_actions", fallback["improvement_actions"]),
        }
    except Exception:
        return fallback


def generate_portfolio_artifacts(payload: dict) -> dict:
    fallback = {
        "resume_bullets": [
            "Designed an automation blueprint that reduced manual process overhead through rule-based routing.",
            "Defined KPI-based rollout criteria and exception handling safeguards for production reliability.",
        ],
        "linkedin_post": "Built an end-to-end automation project from process mapping to KPI-driven design review.",
        "project_summary": "This project identifies bottlenecks, proposes a future-state automation flow, and defines measurable outcomes.",
        "architecture_overview": "Intake -> Validation -> Decisioning -> Automation Tasks -> Human Review -> Reporting Dashboard",
    }

    settings = get_settings()
    client = _build_azure_client()
    if client is None:
        return fallback

    try:
        completion = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            temperature=0.35,
            max_tokens=600,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate portfolio artifacts for a process automation project. "
                        "Return strictly valid JSON with keys: resume_bullets, linkedin_post, project_summary, architecture_overview."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(payload),
                },
            ],
        )
        content = completion.choices[0].message.content or ""
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            return fallback
        return {
            "resume_bullets": parsed.get("resume_bullets", fallback["resume_bullets"]),
            "linkedin_post": parsed.get("linkedin_post", fallback["linkedin_post"]),
            "project_summary": parsed.get("project_summary", fallback["project_summary"]),
            "architecture_overview": parsed.get("architecture_overview", fallback["architecture_overview"]),
        }
    except Exception:
        return fallback
