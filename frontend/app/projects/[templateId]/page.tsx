"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "../../../lib/auth";

type ProjectTemplateDetail = {
  id: string;
  title: string;
  difficulty: string;
  industry: string;
  problem_statement: string;
  business_goal: string;
  rubric: Array<{ key: string; weight: number }>;
};

type ProjectSubmissionDetail = {
  id: string;
  title: string;
  review_feedback: {
    rubric_scores: Record<string, number>;
    summary: string;
    improvement_actions: string[];
  } | null;
  portfolio_artifacts: {
    resume_bullets: string[];
    linkedin_post: string;
    project_summary: string;
    architecture_overview: string;
  } | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function ProjectWorkspacePage() {
  const params = useParams<{ templateId: string }>();
  const templateId = params.templateId;
  const { authHeaders, isAuthenticated } = useAuth();
  const [template, setTemplate] = useState<ProjectTemplateDetail | null>(null);
  const [status, setStatus] = useState("Loading template...");
  const [submission, setSubmission] = useState<ProjectSubmissionDetail | null>(null);
  const [form, setForm] = useState({
    title: "",
    current_process: "",
    proposed_automation: "",
    success_metrics: "",
    risk_controls: ""
  });

  useEffect(() => {
    const loadTemplate = async () => {
      const response = await fetch(`${API_BASE}/project-templates/${templateId}`);
      if (!response.ok) {
        setStatus("Template not found.");
        return;
      }
      const data = (await response.json()) as ProjectTemplateDetail;
      setTemplate(data);
      setForm((current) => ({ ...current, title: data.title }));
      setStatus("Template loaded.");
    };
    void loadTemplate();
  }, [templateId]);

  const createSubmission = async () => {
    if (!isAuthenticated) {
      setStatus("Login first to submit projects.");
      return;
    }
    setStatus("Saving submission...");
    const response = await fetch(`${API_BASE}/project-submissions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify({ template_id: templateId, ...form })
    });
    if (!response.ok) {
      setStatus("Failed to create submission.");
      return;
    }
    const data = (await response.json()) as ProjectSubmissionDetail;
    setSubmission(data);
    setStatus("Submission created.");
  };

  const runReview = async () => {
    if (!submission) {
      setStatus("Create a submission first.");
      return;
    }
    setStatus("Running AI review...");
    const response = await fetch(`${API_BASE}/project-submissions/${submission.id}/review`, {
      method: "POST",
      headers: { ...authHeaders }
    });
    if (!response.ok) {
      setStatus("Review failed.");
      return;
    }
    const review = await response.json();
    setSubmission((current) => (current ? { ...current, review_feedback: review } : current));
    setStatus("Review complete.");
  };

  const generateArtifacts = async () => {
    if (!submission) {
      setStatus("Create a submission first.");
      return;
    }
    setStatus("Generating portfolio artifacts...");
    const response = await fetch(`${API_BASE}/project-submissions/${submission.id}/artifacts`, {
      method: "POST",
      headers: { ...authHeaders }
    });
    if (!response.ok) {
      setStatus("Artifact generation failed.");
      return;
    }
    const artifacts = await response.json();
    setSubmission((current) => (current ? { ...current, portfolio_artifacts: artifacts } : current));
    setStatus("Artifacts generated.");
  };

  return (
    <section>
      <h1>Project Workspace</h1>
      <p style={{ color: "#475569" }}>{status}</p>

      {template ? (
        <article style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
          <h3 style={{ marginTop: 0 }}>{template.title}</h3>
          <p>{template.problem_statement}</p>
          <p>
            <strong>Goal:</strong> {template.business_goal}
          </p>
        </article>
      ) : null}

      <div style={{ display: "grid", gap: 8, marginTop: 14 }}>
        <input
          value={form.title}
          onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
          placeholder="Submission title"
          style={{ padding: "8px 10px" }}
        />
        <textarea
          value={form.current_process}
          onChange={(event) => setForm((current) => ({ ...current, current_process: event.target.value }))}
          placeholder="Current process (as-is)"
          rows={4}
          style={{ padding: "8px 10px" }}
        />
        <textarea
          value={form.proposed_automation}
          onChange={(event) => setForm((current) => ({ ...current, proposed_automation: event.target.value }))}
          placeholder="Proposed automation (to-be)"
          rows={4}
          style={{ padding: "8px 10px" }}
        />
        <textarea
          value={form.success_metrics}
          onChange={(event) => setForm((current) => ({ ...current, success_metrics: event.target.value }))}
          placeholder="Success metrics (KPI baseline and target)"
          rows={3}
          style={{ padding: "8px 10px" }}
        />
        <textarea
          value={form.risk_controls}
          onChange={(event) => setForm((current) => ({ ...current, risk_controls: event.target.value }))}
          placeholder="Risk controls + human-in-the-loop plan"
          rows={3}
          style={{ padding: "8px 10px" }}
        />
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button onClick={createSubmission} disabled={!isAuthenticated} style={{ padding: "8px 12px" }}>
          Save submission
        </button>
        <button onClick={runReview} disabled={!submission || !isAuthenticated} style={{ padding: "8px 12px" }}>
          Run AI review
        </button>
        <button
          onClick={generateArtifacts}
          disabled={!submission || !isAuthenticated}
          style={{ padding: "8px 12px" }}
        >
          Generate portfolio artifacts
        </button>
      </div>

      {submission?.review_feedback ? (
        <article style={{ marginTop: 14, background: "#fff", border: "1px solid #e2e8f0", padding: 12 }}>
          <h4>AI Review</h4>
          <p>{submission.review_feedback.summary}</p>
          <pre style={{ whiteSpace: "pre-wrap" }}>
            {JSON.stringify(submission.review_feedback.rubric_scores, null, 2)}
          </pre>
          <ul>
            {submission.review_feedback.improvement_actions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      ) : null}

      {submission?.portfolio_artifacts ? (
        <article style={{ marginTop: 14, background: "#fff", border: "1px solid #e2e8f0", padding: 12 }}>
          <h4>Portfolio Artifacts</h4>
          <p>
            <strong>Project summary:</strong> {submission.portfolio_artifacts.project_summary}
          </p>
          <p>
            <strong>Architecture:</strong> {submission.portfolio_artifacts.architecture_overview}
          </p>
          <p>
            <strong>LinkedIn draft:</strong> {submission.portfolio_artifacts.linkedin_post}
          </p>
          <h5>Resume bullets</h5>
          <ul>
            {submission.portfolio_artifacts.resume_bullets.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      ) : null}
    </section>
  );
}
