/**
 * Custom hook for trading analysis
 */
"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { AnalysisRequest, AnalysisResponse } from "@/lib/types";

export function useAnalysis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const runAnalysis = async (request: AnalysisRequest) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.runAnalysis(request);
      setResult(response);
      return response;
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || "Analysis failed";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setLoading(false);
    setError(null);
    setResult(null);
  };

  return {
    runAnalysis,
    loading,
    error,
    result,
    reset,
  };
}
