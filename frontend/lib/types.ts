/**
 * TypeScript type definitions for TradingAgents API
 */

export interface AnalysisRequest {
  ticker: string;
  analysis_date: string;
  analysts?: string[];
  research_depth?: number;
  deep_think_llm?: string;
  quick_think_llm?: string;
}

export interface AnalysisResponse {
  status: "success" | "error" | "processing";
  ticker: string;
  analysis_date: string;
  decision?: Decision;
  reports?: Reports;
  error?: string;
}

export interface Decision {
  action: string;
  quantity?: number;
  reasoning?: string;
  confidence?: number;
}

export interface Reports {
  market_report?: string;
  sentiment_report?: string;
  news_report?: string;
  fundamentals_report?: string;
  investment_plan?: string;
  trader_investment_plan?: string;
  final_trade_decision?: string;
  investment_debate_state?: DebateState;
  risk_debate_state?: DebateState;
}

export interface DebateState {
  bull_history?: string;
  bear_history?: string;
  risky_history?: string;
  safe_history?: string;
  neutral_history?: string;
  judge_decision?: string;
}

export interface ConfigResponse {
  available_analysts: string[];
  available_llms: {
    [provider: string]: string[];
  };
  default_config: {
    [key: string]: any;
  };
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface Ticker {
  symbol: string;
  name: string;
}
