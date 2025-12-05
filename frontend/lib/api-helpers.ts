/**
 * Helper functions for API configuration
 */

import { ApiSettings } from "./storage";

/**
 * Get the base URL for a given LLM model
 * If custom_base_url is set, it takes precedence
 */
export function getBaseUrlForModel(model: string, customBaseUrl?: string): string {
  // If custom base URL is provided, use it
  if (customBaseUrl && customBaseUrl.trim() !== "") {
    return customBaseUrl;
  }

  // OpenAI models
  if (
    model.startsWith("gpt-") ||
    model.startsWith("o4-") ||
    model.startsWith("o1-")
  ) {
    return "https://api.openai.com/v1";
  }

  // Anthropic models
  if (model.startsWith("claude-")) {
    return "https://api.anthropic.com";
  }

  // Google models
  if (model.startsWith("gemini-")) {
    return "https://generativelanguage.googleapis.com/v1beta/openai";
  }

  // Grok models
  if (model.startsWith("grok-")) {
    return "https://api.x.ai/v1";
  }

  // DeepSeek models
  if (model.startsWith("deepseek-")) {
    return "https://api.deepseek.com/v1";
  }

  // Qwen models
  if (model.startsWith("qwen")) {
    return "https://dashscope-intl.aliyuncs.com/compatible-mode/v1";
  }

  // Default to OpenAI
  return "https://api.openai.com/v1";
}

/**
 * Get the API key for a given LLM model from saved settings
 * If custom_base_url is set and custom_api_key exists, use custom key
 */
export function getApiKeyForModel(
  model: string,
  settings: ApiSettings
): string {
  // If custom base URL is configured and has a key, use the custom key
  if (settings.custom_base_url && settings.custom_base_url.trim() !== "") {
    if (settings.custom_api_key && settings.custom_api_key.trim() !== "") {
      return settings.custom_api_key;
    }
  }

  // OpenAI models
  if (
    model.startsWith("gpt-") ||
    model.startsWith("o4-") ||
    model.startsWith("o1-")
  ) {
    return settings.openai_api_key;
  }

  // Anthropic models
  if (model.startsWith("claude-")) {
    return settings.anthropic_api_key || "";
  }

  // Google models
  if (model.startsWith("gemini-")) {
    return settings.google_api_key || "";
  }

  // Grok models
  if (model.startsWith("grok-")) {
    return settings.grok_api_key || "";
  }

  // DeepSeek models
  if (model.startsWith("deepseek-")) {
    return settings.deepseek_api_key || "";
  }

  // Qwen models
  if (model.startsWith("qwen")) {
    return settings.qwen_api_key || "";
  }

  // Default to OpenAI
  return settings.openai_api_key;
}
