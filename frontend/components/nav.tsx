"use client";

import Link from "next/link";
import { useAuth } from "../lib/auth";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/learn", label: "Learning Path" },
  { href: "/workflows", label: "Workflow Lab" }
];

export function TopNav() {
  const { isAuthenticated, mode, logout } = useAuth();

  return (
    <header
      style={{
        padding: "16px 24px",
        borderBottom: "1px solid #e2e8f0",
        background: "#ffffff",
        position: "sticky",
        top: 0
      }}
    >
      <nav
        style={{
          display: "flex",
          gap: 16,
          maxWidth: 960,
          margin: "0 auto",
          alignItems: "center"
        }}
      >
        <strong>Process AI Academy</strong>
        {navItems.map((item) => (
          <Link key={item.href} href={item.href}>
            {item.label}
          </Link>
        ))}
        <span style={{ marginLeft: "auto", color: "#475569" }}>Auth: {mode}</span>
        {!isAuthenticated ? (
          <Link href="/login">Login</Link>
        ) : (
          <button onClick={logout} style={{ padding: "6px 10px" }}>
            Logout
          </button>
        )}
      </nav>
    </header>
  );
}
