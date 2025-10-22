import React, { useState, type ReactNode } from "react";
import { AppContext, type HistoryItem } from "./AppContext";

export const AppProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [currentResult, setCurrentResult] = useState<HistoryItem | null>(null);

  return (
    <AppContext.Provider
      value={{ currentResult, setCurrentResult, history, setHistory }}
    >
      {children}
    </AppContext.Provider>
  );
};
