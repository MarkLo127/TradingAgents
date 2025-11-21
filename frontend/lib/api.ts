/**
 * API client for TradingAgents backend
 */
import axios from "axios";
import type {
  AnalysisRequest,
  AnalysisResponse,
  ConfigResponse,
  HealthResponse,
  Ticker,
} from "./types";

const apiClient = axios.create({
  headers: {
    "Content-Type": "application/json",
  },
});

export const api = {
  /**
   * Get API health status
   */
  async health(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>("/api/health");
    return response.data;
  },

  /**
   * Get configuration options
   */
  async getConfig(): Promise<ConfigResponse> {
    const response = await apiClient.get<ConfigResponse>("/api/config");
    return response.data;
  },

  /**
   * Run trading analysis
   */
  async runAnalysis(request: AnalysisRequest): Promise<AnalysisResponse> {
    const response = await apiClient.post<AnalysisResponse>(
      "/api/analyze",
      request
    );
    return response.data;
  },

  /**
   * Get list of popular tickers
   */
  async getTickers(): Promise<{ tickers: Ticker[] }> {
    const response = await apiClient.get<{ tickers: Ticker[] }>("/api/tickers");
    return response.data;
  },
};
