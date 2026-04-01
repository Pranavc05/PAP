from app.models import TutorGenerateRequest


def _clean_text(value: str) -> str:
    return " ".join(value.strip().split())


def generate_tutor_response(request: TutorGenerateRequest) -> str:
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
