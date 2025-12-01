import { createContext } from "react";
import type React from "react";

export interface Result {
  model: string;
  confidence: number;
}

export interface HistoryItem {
  image: string | undefined;
  filename?: string;
  results: Result[];
  analysis: Result;
}

export interface AppContextType {
  history: HistoryItem[];
  setHistory: React.Dispatch<React.SetStateAction<HistoryItem[]>>;
  currentResult: HistoryItem | null;
  setCurrentResult: React.Dispatch<React.SetStateAction<HistoryItem | null>>;
  refreshHistory: () => Promise<void>;
}

export const AppContext = createContext<AppContextType | undefined>(undefined);
