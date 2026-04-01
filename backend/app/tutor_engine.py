from functools import lru_cache

from openai import AzureOpenAI

from app.config import get_settings
from app.models import TutorGenerateRequest


def _clean_text(value: str) -> str:
    return " ".join(value.strip().split())


def _fallback_response(request: TutorGenerateRequest) -> str:
    learner_text = _clean_text(request.user_message)
    lesson_context = _clean_text(request.lesson_context or "")
    mode = request.mode.lower().strip()
    hint_level = max(1, min(request.hint_level, 3))

    if mode == "socratic":
        prompts = [
            "What is the current process, step-by-step, before automation?",
            "Which steps are repetitive and rules-based versus judgment-heavy?",
            "What measurable outcome (time, error rate, cost) are you trying to improve?",
        ]
        return (
            "Good direction. Let's reason it out instead of jumping straight to tools.\n"
            f"- Your focus: {learner_text}\n"
            f"- Lesson context: {lesson_context or 'general process automation'}\n"
            f"Start with this question: {prompts[(len(learner_text) + hint_level) % len(prompts)]}"
        )

    if mode == "hint":
        hints = {
            1: "Hint 1: Break the workflow into inputs, decisions, and outputs first.",
            2: "Hint 2: Mark each step as repetitive, rule-based, or human-judgment required.",
            3: "Hint 3: Design a pilot with one KPI (e.g., cycle time) and one safeguard (human review).",
        }
        return (
            f"{hints[hint_level]}\n"
            f"Use this on your case: {learner_text}\n"
            "If you want, ask for the next hint level for more direct guidance."
        )

    return (
        "Here's a concise explanation:\n"
        f"- Topic: {learner_text}\n"
        f"- Context: {lesson_context or 'process automation fundamentals'}\n"
        "- Practical rule: automate stable, repetitive, high-volume steps first; keep exceptions and low-confidence cases with human review.\n"
        "- Next action: draft the current-state map, define one KPI, then design the future-state flow."
    )


@lru_cache
def _get_azure_client(api_key: str, endpoint: str, api_version: str) -> AzureOpenAI:
    return AzureOpenAI(api_key=api_key, azure_endpoint=endpoint, api_version=api_version)


def _build_system_prompt(mode: str, hint_level: int) -> str:
    return (
        "You are an AI tutor for process automation learners.\n"
        f"Mode: {mode}\n"
        f"Hint Level: {hint_level}\n"
        "Rules:\n"
        "- Do not jump straight to tools.\n"
        "- Prefer guiding questions in Socratic mode.\n"
        "- For Hint mode, reveal only the requested level of detail.\n"
        "- Keep responses practical, concise, and business-aware.\n"
        "- Encourage measurable outcomes and human-in-the-loop safeguards."
    )


def generate_tutor_response(request: TutorGenerateRequest) -> str:
    settings = get_settings()
    if settings.ai_provider.lower().strip() != "azure_openai":
        return _fallback_response(request)

    required_values = [
        settings.azure_openai_api_key,
        settings.azure_openai_endpoint,
        settings.azure_openai_api_version,
        settings.azure_openai_deployment,
    ]
    if not all(value.strip() for value in required_values):
        return _fallback_response(request)

    mode = request.mode.lower().strip()
    hint_level = max(1, min(request.hint_level, 3))
    lesson_context = _clean_text(request.lesson_context or "")
    learner_text = _clean_text(request.user_message)

    try:
        client = _get_azure_client(
            settings.azure_openai_api_key,
            settings.azure_openai_endpoint,
            settings.azure_openai_api_version,
        )
        completion = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            temperature=0.4,
            max_tokens=320,
            messages=[
                {"role": "system", "content": _build_system_prompt(mode, hint_level)},
                {
                    "role": "user",
                    "content": (
                        f"Learner message: {learner_text}\n"
                        f"Lesson context: {lesson_context or 'General process automation'}"
                    ),
                },
            ],
        )
        content = completion.choices[0].message.content
        return content.strip() if content else _fallback_response(request)
    except Exception:
        return _fallback_response(request)
