"use client";

import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../../lib/auth";

type QuizOption = {
  key: string;
  text: string;
};

type QuizQuestion = {
  id: string;
  prompt: string;
  options: QuizOption[];
  position: number;
};

type QuizResultItem = {
  question_id: string;
  selected_option_key: string | null;
  correct_option_key: string;
  is_correct: boolean;
  explanation: string;
};

type QuizSubmitResponse = {
  attempt_id: string;
  score: number;
  total_questions: number;
  percentage: number;
  results: QuizResultItem[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function LessonQuizPage() {
  const params = useParams<{ lessonId: string }>();
  const lessonId = params.lessonId;
  const { authHeaders, isAuthenticated, mode } = useAuth();
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [status, setStatus] = useState("Loading quiz...");
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizSubmitResponse | null>(null);

  useEffect(() => {
    const loadQuiz = async () => {
      try {
        const response = await fetch(`${API_BASE}/lessons/${lessonId}/quiz`);
        if (!response.ok) {
          setStatus("Quiz not found for this lesson.");
          return;
        }
        const data = (await response.json()) as QuizQuestion[];
        setQuestions(data);
        setStatus(data.length ? "Quiz ready" : "No quiz questions configured.");
      } catch {
        setStatus("Failed to load quiz.");
      }
    };
    void loadQuiz();
  }, [lessonId]);

  const answeredCount = useMemo(
    () => questions.filter((question) => Boolean(answers[question.id])).length,
    [questions, answers]
  );

  const submitQuiz = async () => {
    if (!isAuthenticated) {
      setStatus(`Not authenticated in ${mode} mode.`);
      return;
    }
    setStatus("Submitting quiz...");
    const payload = {
      answers: questions
        .filter((question) => answers[question.id])
        .map((question) => ({
          question_id: question.id,
          selected_option_key: answers[question.id]
        }))
    };
    const response = await fetch(`${API_BASE}/lessons/${lessonId}/quiz/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      setStatus("Quiz submission failed.");
      return;
    }
    const data = (await response.json()) as QuizSubmitResponse;
    setResult(data);
    setStatus("Quiz submitted.");
  };

  return (
    <section>
      <h1>Lesson Quiz</h1>
      <p>Lesson ID: {lessonId}</p>
      <p style={{ color: "#475569" }}>
        {status} • Answered {answeredCount}/{questions.length}
      </p>

      <div style={{ display: "grid", gap: 14 }}>
        {questions.map((question) => (
          <article key={question.id} style={{ background: "#fff", border: "1px solid #e2e8f0", padding: 12 }}>
            <p style={{ margin: "0 0 8px 0" }}>
              <strong>Q{question.position}.</strong> {question.prompt}
            </p>
            <div style={{ display: "grid", gap: 6 }}>
              {question.options.map((option) => (
                <label key={option.key} style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    checked={answers[question.id] === option.key}
                    onChange={() => setAnswers((current) => ({ ...current, [question.id]: option.key }))}
                  />
                  <span>{option.text}</span>
                </label>
              ))}
            </div>
          </article>
        ))}
      </div>

      <button onClick={submitQuiz} disabled={!isAuthenticated || !questions.length} style={{ marginTop: 16, padding: "8px 12px" }}>
        Submit quiz
      </button>

      {result ? (
        <article style={{ marginTop: 16, background: "#fff", border: "1px solid #e2e8f0", padding: 14 }}>
          <h3>
            Score: {result.score}/{result.total_questions} ({result.percentage}%)
          </h3>
          <ul>
            {result.results.map((item) => (
              <li key={item.question_id}>
                {item.is_correct ? "Correct" : "Incorrect"} — correct option: {item.correct_option_key}.{" "}
                {item.explanation}
              </li>
            ))}
          </ul>
        </article>
      ) : null}
    </section>
  );
}
