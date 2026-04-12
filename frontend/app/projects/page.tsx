"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "../../lib/auth";

type ProjectTemplateSummary = {
  id: string;
  slug: string;
  title: string;
  difficulty: string;
  industry: string;
  business_goal: string;
};

type ProjectSubmissionOverview = {
  id: string;
  template_id: string;
  template_title: string;
  title: string;
  created_at: string;
  updated_at: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function ProjectsPage() {
  const { authHeaders, isAuthenticated } = useAuth();
  const [templates, setTemplates] = useState<ProjectTemplateSummary[]>([]);
  const [submissions, setSubmissions] = useState<ProjectSubmissionOverview[]>([]);
  const [status, setStatus] = useState("Loading projects...");

  useEffect(() => {
    const load = async () => {
      try {
        const templateResponse = await fetch(`${API_BASE}/project-templates`);
        if (!templateResponse.ok) {
          setStatus("Failed to load project templates.");
          return;
        }
        const templateData = (await templateResponse.json()) as ProjectTemplateSummary[];
        setTemplates(templateData);

        if (isAuthenticated) {
          const submissionResponse = await fetch(`${API_BASE}/project-submissions`, {
            headers: { ...authHeaders }
          });
          if (submissionResponse.ok) {
            const submissionData = (await submissionResponse.json()) as ProjectSubmissionOverview[];
            setSubmissions(submissionData);
          }
        }
        setStatus("Project templates loaded.");
      } catch {
        setStatus("Backend unavailable.");
      }
    };
    void load();
  }, [isAuthenticated]);

  return (
    <section>
      <h1>Project Tracks</h1>
      <p>Choose a template, build your solution, then generate portfolio artifacts.</p>
      <p style={{ color: "#475569" }}>{status}</p>

      <h3>Templates</h3>
      <div style={{ display: "grid", gap: 12, marginBottom: 20 }}>
        {templates.map((template) => (
          <article
            key={template.id}
            style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}
          >
            <h4 style={{ margin: "0 0 6px 0" }}>{template.title}</h4>
            <p style={{ margin: "0 0 8px 0" }}>{template.business_goal}</p>
            <small>
              {template.difficulty} • {template.industry}
            </small>
            <div style={{ marginTop: 8 }}>
              <Link href={`/projects/${template.id}`}>Open project workspace</Link>
            </div>
          </article>
        ))}
      </div>

      <h3>Your submissions</h3>
      <div style={{ display: "grid", gap: 10 }}>
        {submissions.map((submission) => (
          <article
            key={submission.id}
            style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 10 }}
          >
            <strong>{submission.title}</strong>
            <div style={{ fontSize: 13, color: "#475569" }}>{submission.template_title}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              Updated {new Date(submission.updated_at).toLocaleString()}
            </div>
          </article>
        ))}
        {!submissions.length ? <p style={{ color: "#64748b" }}>No submissions yet.</p> : null}
      </div>
    </section>
  );
}
