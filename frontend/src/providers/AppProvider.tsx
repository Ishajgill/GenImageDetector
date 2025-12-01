import React, { useState, useEffect, useContext, type ReactNode } from "react";
import { AppContext, type HistoryItem } from "../contexts/AppContext";
import { AuthContext } from "../contexts/AuthContext";

const STORAGE_KEY = "anonymous_history";

export const AppProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [currentResult, setCurrentResult] = useState<HistoryItem | null>(null);
  const authContext = useContext(AuthContext);

  // Load history on mount - either from localStorage (anonymous) or backend (logged in)
  useEffect(() => {
    if (authContext?.loading) return;

    if (authContext?.user && authContext?.token) {
      // User is logged in - fetch history from backend
      fetchHistoryFromBackend(authContext.token);
    } else {
      // Anonymous user - load from localStorage
      loadLocalHistory();
    }
  }, [authContext?.user, authContext?.token, authContext?.loading]);

  // Save to localStorage for anonymous users whenever history changes
  useEffect(() => {
    if (authContext?.loading) return;

    if (!authContext?.user) {
      // Save to localStorage only for anonymous users
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    }
  }, [history, authContext?.user, authContext?.loading]);

  const loadLocalHistory = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setHistory(parsed);
      }
    } catch (err) {
      console.error("Failed to load history from localStorage:", err);
    }
  };

  const fetchHistoryFromBackend = async (token: string) => {
    try {
      const res = await fetch("http://localhost:8000/history", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.ok) {
        const data = await res.json();
        // Transform backend format to frontend format
        const transformedHistory: HistoryItem[] = data.map((item: any) => ({
          image: item.image_data,
          filename: item.filename,
          results: item.model_results.map((mr: any) => ({
            model: mr.model_name,
            confidence: mr.confidence,
          })),
          analysis: {
            model: "Aggregate",
            confidence: item.aggregate_confidence,
          },
        }));
        setHistory(transformedHistory);
      }
    } catch (err) {
      console.error("Failed to fetch history from backend:", err);
    }
  };

  const refreshHistory = async () => {
    if (authContext?.user && authContext?.token) {
      await fetchHistoryFromBackend(authContext.token);
    }
  };

  return (
    <AppContext.Provider
      value={{
        currentResult,
        setCurrentResult,
        history,
        setHistory,
        refreshHistory,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};
