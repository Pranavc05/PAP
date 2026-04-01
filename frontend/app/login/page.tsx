"use client";

import { useState } from "react";
import { useAuth } from "../../lib/auth";

export default function LoginPage() {
  const { mode, isAuthenticated, devUserId, updateDevUserId, loginWithToken } = useAuth();
  const [userIdInput, setUserIdInput] = useState(devUserId);
  const [tokenInput, setTokenInput] = useState("");
  const [status, setStatus] = useState("");

  const saveDevSession = () => {
    updateDevUserId(userIdInput);
    setStatus("Dev session saved.");
  };

  const saveTokenSession = () => {
    if (!tokenInput.trim()) {
      setStatus("Enter an access token first.");
      return;
    }
    loginWithToken(tokenInput);
    setStatus("Token session saved.");
    setTokenInput("");
  };

  return (
    <section>
      <h1>Login</h1>
      <p>Current auth mode: {mode}</p>
      <p>Status: {isAuthenticated ? "Authenticated" : "Not authenticated"}</p>

      {mode === "dev" ? (
        <div style={{ display: "grid", gap: 8, maxWidth: 520 }}>
          <label htmlFor="dev-user-id">Developer user ID</label>
          <input
            id="dev-user-id"
            value={userIdInput}
            onChange={(event) => setUserIdInput(event.target.value)}
            style={{ padding: "8px 10px" }}
          />
          <button onClick={saveDevSession} style={{ width: "fit-content", padding: "8px 12px" }}>
            Save dev session
          </button>
        </div>
      ) : (
        <div style={{ display: "grid", gap: 8, maxWidth: 520 }}>
          <label htmlFor="access-token">Bearer access token</label>
          <input
            id="access-token"
            type="password"
            value={tokenInput}
            onChange={(event) => setTokenInput(event.target.value)}
            placeholder="Paste provider access token"
            style={{ padding: "8px 10px" }}
          />
          <button onClick={saveTokenSession} style={{ width: "fit-content", padding: "8px 12px" }}>
            Save token session
          </button>
        </div>
      )}

      {status ? <p style={{ marginTop: 12, color: "#475569" }}>{status}</p> : null}
    </section>
  );
}
