"use client";

import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../lib/auth";

type TutorSessionOverview = {
  id: string;
  lesson_id: string | null;
  title: string;
  mode: string;
  created_at: string;
  updated_at: string;
};

type TutorMessage = {
  id: string;
  role: string;
  content: string;
  hint_level: number | null;
  created_at: string;
};

type TutorSessionDetail = {
  session: TutorSessionOverview;
  messages: TutorMessage[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function TutorPage() {
  const { authHeaders, isAuthenticated } = useAuth();
  const [sessions, setSessions] = useState<TutorSessionOverview[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<TutorMessage[]>([]);
  const [status, setStatus] = useState("Create a tutor session to begin.");
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("socratic");
  const [hintLevel, setHintLevel] = useState(1);

  const activeSession = useMemo(() => sessions.find((item) => item.id === sessionId) ?? null, [sessions, sessionId]);

  const loadSessions = async () => {
    if (!isAuthenticated) {
      setStatus("Login first to use AI Tutor.");
      return;
    }
    const response = await fetch(`${API_BASE}/tutor/sessions`, { headers: { ...authHeaders } });
    if (!response.ok) {
      setStatus("Failed to load tutor sessions.");
      return;
    }
    const data = (await response.json()) as TutorSessionOverview[];
    setSessions(data);
  };

  useEffect(() => {
    void loadSessions();
  }, [isAuthenticated]);

  const createSession = async () => {
    if (!isAuthenticated) {
      setStatus("Login first to create a session.");
      return;
    }
    const response = await fetch(`${API_BASE}/tutor/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify({ title: "Guided AI Tutor", mode })
    });
    if (!response.ok) {
      setStatus("Failed to create tutor session.");
      return;
    }
    const created = (await response.json()) as TutorSessionOverview;
    setSessions((current) => [created, ...current]);
    setSessionId(created.id);
    setMessages([]);
    setStatus("Tutor session created.");
  };

  const selectSession = async (nextSessionId: string) => {
    setSessionId(nextSessionId);
    const response = await fetch(`${API_BASE}/tutor/sessions/${nextSessionId}`, {
      headers: { ...authHeaders }
    });
    if (!response.ok) {
      setStatus("Failed to load tutor messages.");
      return;
    }
    const detail = (await response.json()) as TutorSessionDetail;
    setMessages(detail.messages);
    setStatus(`Loaded session: ${detail.session.title}`);
  };

  const sendMessage = async () => {
    if (!sessionId) {
      setStatus("Create or select a session first.");
      return;
    }
    if (!input.trim()) {
      return;
    }
    setStatus("Tutor is thinking...");
    const response = await fetch(`${API_BASE}/tutor/sessions/${sessionId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders },
      body: JSON.stringify({
        content: input,
        mode,
        hint_level: hintLevel
      })
    });
    if (!response.ok) {
      setStatus("Failed to send message.");
      return;
    }
    const data = (await response.json()) as { user_message: TutorMessage; assistant_message: TutorMessage };
    setMessages((current) => [...current, data.user_message, data.assistant_message]);
    setInput("");
    setStatus("Tutor response received.");
    await loadSessions();
  };

  return (
    <section>
      <h1>AI Tutor</h1>
      <p>Guided tutor with Socratic, Hint, and Explain coaching modes.</p>
      <p style={{ color: "#475569" }}>{status}</p>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button onClick={createSession} disabled={!isAuthenticated} style={{ padding: "8px 12px" }}>
          New session
        </button>
        <select value={mode} onChange={(event) => setMode(event.target.value)} style={{ padding: "8px 10px" }}>
          <option value="socratic">Socratic</option>
          <option value="hint">Hint</option>
          <option value="explain">Explain</option>
        </select>
        <select
          value={hintLevel}
          onChange={(event) => setHintLevel(Number(event.target.value))}
          style={{ padding: "8px 10px" }}
        >
          <option value={1}>Hint Level 1</option>
          <option value={2}>Hint Level 2</option>
          <option value={3}>Hint Level 3</option>
        </select>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 12 }}>
        <aside style={{ border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", padding: 10 }}>
          <h3 style={{ marginTop: 0 }}>Sessions</h3>
          <div style={{ display: "grid", gap: 8 }}>
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => selectSession(session.id)}
                style={{
                  textAlign: "left",
                  padding: "8px 10px",
                  borderRadius: 6,
                  border: session.id === activeSession?.id ? "1px solid #0ea5e9" : "1px solid #cbd5e1",
                  background: "#f8fafc"
                }}
              >
                <strong>{session.title}</strong>
                <div style={{ fontSize: 12, color: "#475569" }}>{session.mode}</div>
              </button>
            ))}
          </div>
        </aside>

        <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", padding: 12 }}>
          <h3 style={{ marginTop: 0 }}>Conversation</h3>
          <div style={{ display: "grid", gap: 8, maxHeight: 420, overflow: "auto", marginBottom: 12 }}>
            {messages.map((message) => (
              <article
                key={message.id}
                style={{
                  border: "1px solid #e2e8f0",
                  borderRadius: 8,
                  padding: 10,
                  background: message.role === "assistant" ? "#eff6ff" : "#f8fafc"
                }}
              >
                <strong style={{ textTransform: "capitalize" }}>{message.role}</strong>
                <p style={{ margin: "6px 0 0 0", whiteSpace: "pre-wrap" }}>{message.content}</p>
              </article>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask the tutor about your process..."
              style={{ flex: 1, padding: "8px 10px" }}
            />
            <button onClick={sendMessage} disabled={!isAuthenticated || !sessionId} style={{ padding: "8px 12px" }}>
              Send
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
