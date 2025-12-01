import React, { useState, useEffect } from "react";
import type { ReactNode } from "react";
import { AuthContext, type User } from "../contexts/AuthContext";

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const storedToken = localStorage.getItem("auth_token");
    if (storedToken) {
      fetchCurrentUser(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async (authToken: string) => {
    try {
      const res = await fetch("http://localhost:8000/auth/me", {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        setToken(authToken);
      } else {
        // Token is invalid
        localStorage.removeItem("auth_token");
        setToken(null);
        setUser(null);
      }
    } catch (err) {
      console.error("Failed to fetch current user:", err);
      localStorage.removeItem("auth_token");
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || "Login failed");
    }

    const data = await res.json();
    const authToken = data.access_token;

    localStorage.setItem("auth_token", authToken);
    setToken(authToken);

    // Migrate any anonymous history before fetching user data
    await migrateAnonymousHistory(authToken);

    // Fetch user data
    await fetchCurrentUser(authToken);
  };

  const signup = async (username: string, password: string) => {
    const res = await fetch("http://localhost:8000/auth/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || "Signup failed");
    }

    const data = await res.json();
    const authToken = data.access_token;

    localStorage.setItem("auth_token", authToken);
    setToken(authToken);

    // Migrate any anonymous history before fetching user data
    await migrateAnonymousHistory(authToken);

    // Fetch user data
    await fetchCurrentUser(authToken);
  };

  const migrateAnonymousHistory = async (authToken: string) => {
    try {
      const STORAGE_KEY = "anonymous_history";
      const stored = localStorage.getItem(STORAGE_KEY);

      if (!stored) return;

      const historyItems = JSON.parse(stored);

      if (!historyItems || historyItems.length === 0) return;

      // Transform history items to migration format
      const migrationItems = historyItems.map(
        (item: {
          image: string;
          filename?: string;
          results: Array<{ model: string; confidence: number }>;
          analysis: { confidence: number };
        }) => ({
          image: item.image,
          filename: item.filename || "migrated-image.jpg",
          aggregate_confidence: item.analysis.confidence,
          model_results: item.results.map((r) => ({
            model_name: r.model,
            confidence: r.confidence,
          })),
        })
      );

      // Send batch migration request
      const res = await fetch("http://localhost:8000/migrate-history", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${authToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ items: migrationItems }),
      });

      if (res.ok) {
        const result = await res.json();
        console.log(`Migration complete: ${result.message}`);
        // Clear localStorage after successful migration
        localStorage.removeItem(STORAGE_KEY);
      } else {
        console.error("Failed to migrate history:", await res.text());
      }
    } catch (err) {
      console.error("Failed to migrate anonymous history:", err);
    }
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    setToken(null);
    setUser(null);
    // Trigger app state reset by dispatching a custom event
    window.dispatchEvent(new Event("auth:logout"));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        signup,
        logout,
        loading,
        migrateAnonymousHistory,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
