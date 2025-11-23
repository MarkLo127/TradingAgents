# 修復模型參數傳遞問題

## 問題描述

用戶在前端選擇了不同的模型（如 Claude、Grok 等），但後端實際調用的一直是 `gpt-5-mini-2025-08-07`。

## 根本原因

前端和後端的 API 欄位命名不一致：

| 前端 (舊)                | 後端 (預期)       |
| ------------------------ | ----------------- |
| `shallow_thinking_agent` | `quick_think_llm` |
| `deep_thinking_agent`    | `deep_think_llm`  |

由於欄位名稱不匹配，後端無法接收到前端發送的模型參數，因此使用了預設值 `gpt-5-mini-2025-08-07`。

## 修復內容

### 1. 更新前端類型定義 (`frontend/lib/types.ts`)

```typescript
// 舊
export interface AnalysisRequest {
  shallow_thinking_agent?: string;
  deep_thinking_agent?: string;
  ...
}

// 新
export interface AnalysisRequest {
  quick_think_llm?: string;
  deep_think_llm?: string;
  quick_think_base_url?: string;
  deep_think_base_url?: string;
  quick_think_api_key?: string;
  deep_think_api_key?: string;
  embedding_base_url?: string;
  embedding_api_key?: string;
  ...
}
```

### 2. 更新表單組件 (`frontend/components/analysis/AnalysisForm.tsx`)

- 更新 `formSchema` 中的欄位定義
- 更新 `defaultValues` 中的欄位名稱
- 更新表單欄位的 `name` 屬性

## 後端參數映射 (`backend/app/models/schemas.py`)

後端 schema 定義：

```python
class AnalysisRequest(BaseModel):
    deep_think_llm: Optional[str] = Field(default="gpt-5-mini-2025-08-07")
    quick_think_llm: Optional[str] = Field(default="gpt-5-mini-2025-08-07")
    quick_think_base_url: Optional[str] = Field(default="https://api.openai.com/v1")
    deep_think_base_url: Optional[str] = Field(default="https://api.openai.com/v1")
    quick_think_api_key: Optional[str] = None
    deep_think_api_key: Optional[str] = None
    embedding_base_url: Optional[str] = Field(default="https://api.openai.com/v1")
    embedding_api_key: Optional[str] = None
```

## 驗證

修復後，前端發送的請求應該正確包含：

- `quick_think_llm`: 用戶選擇的快速思維模型
- `deep_think_llm`: 用戶選擇的深層思維模型
- 對應的 Base URL 和 API Key

後端現在能正確接收並使用這些參數。

## 額外修正

同時移除了 Google Gemini 的 API 端點選項，因為項目不再使用 Gemini 服務。
