"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

type AuthMode = "dev" | "oidc";

type AuthContextValue = {
  mode: AuthMode;
  isAuthenticated: boolean;
  token: string;
  devUserId: string;
  authHeaders: HeadersInit;
  loginWithToken: (nextToken: string) => void;
  updateDevUserId: (nextUserId: string) => void;
  logout: () => void;
};

const AUTH_MODE = (process.env.NEXT_PUBLIC_AUTH_MODE ?? "dev") as AuthMode;
const DEFAULT_DEV_USER = process.env.NEXT_PUBLIC_DEV_USER_ID ?? "dev-user";
const TOKEN_KEY = "process_automation_auth_token";
const DEV_USER_KEY = "process_automation_dev_user";

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState("");
  const [devUserId, setDevUserId] = useState(DEFAULT_DEV_USER);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const storedToken = window.localStorage.getItem(TOKEN_KEY);
    const storedDevUser = window.localStorage.getItem(DEV_USER_KEY);
    if (storedToken) {
      setToken(storedToken);
    }
    if (storedDevUser) {
      setDevUserId(storedDevUser);
    }
  }, []);

  const value = useMemo<AuthContextValue>(() => {
    const isAuthenticated = AUTH_MODE === "dev" ? Boolean(devUserId.trim()) : Boolean(token.trim());
    const authHeaders: HeadersInit =
      AUTH_MODE === "dev"
        ? { "X-Dev-User-Id": devUserId }
        : token.trim()
          ? { Authorization: `Bearer ${token.trim()}` }
          : {};

    return {
      mode: AUTH_MODE,
      isAuthenticated,
      token,
      devUserId,
      authHeaders,
      loginWithToken: (nextToken: string) => {
        const trimmed = nextToken.trim();
        setToken(trimmed);
        if (typeof window !== "undefined") {
          window.localStorage.setItem(TOKEN_KEY, trimmed);
        }
      },
      updateDevUserId: (nextUserId: string) => {
        const trimmed = nextUserId.trim() || DEFAULT_DEV_USER;
        setDevUserId(trimmed);
        if (typeof window !== "undefined") {
          window.localStorage.setItem(DEV_USER_KEY, trimmed);
        }
      },
      logout: () => {
        setToken("");
        if (typeof window !== "undefined") {
          window.localStorage.removeItem(TOKEN_KEY);
        }
      }
    };
  }, [token, devUserId]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
