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
  TaskCreatedResponse,
  TaskStatusResponse,
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
   * Start analysis (returns task ID)
   */
  async runAnalysis(request: AnalysisRequest): Promise<TaskCreatedResponse> {
    const response = await apiClient.post<TaskCreatedResponse>(
      "/api/analyze",
      request
    );
    return response.data;
  },

  /**
   * Get task status
   */
  async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    const response = await apiClient.get<TaskStatusResponse>(`/api/task/${taskId}`);
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
