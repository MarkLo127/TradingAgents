"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import type { AnalysisResponse } from "@/lib/types";

interface AnalysisContextType {
  analysisResult: AnalysisResponse | null;
  setAnalysisResult: (result: AnalysisResponse | null) => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(
  undefined
);

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(
    null
  );

  return (
    <AnalysisContext.Provider value={{ analysisResult, setAnalysisResult }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysisContext() {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error("useAnalysisContext must be used within AnalysisProvider");
  }
  return context;
}
