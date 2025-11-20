/**
 * Custom hook for fetching configuration
 */
"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { ConfigResponse } from "@/lib/types";

export function useConfig() {
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await api.getConfig();
        setConfig(response);
      } catch (err: any) {
        setError(err.message || "Failed to fetch configuration");
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  return { config, loading, error };
}
