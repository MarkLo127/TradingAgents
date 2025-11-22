# TradingAgents - 多代理交易分析系統

<div align="center">

**基於 LangGraph 的智能股票交易分析平台，結合多個 AI 代理進行協作決策**

[![GitHub](https://img.shields.io/badge/GitHub-MarkLo127/TradingAgents-blue?logo=github)](https://github.com/MarkLo127/TradingAgents)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

</div>

## 📖 簡介

**TradingAgents** 是一個先進的多代理 AI 交易分析系統，模擬真實世界的交易公司運作模式。透過 LangGraph 編排多個專業化的 AI 代理（分析師、研究員、交易員、風險管理者），系統能夠從不同角度分析股票市場，並通過結構化的辯論與協作流程產生高質量的交易決策。

> 💡 **致敬原作**: 本專案基於 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 進行改進和擴展，加入了完整的 Web 前端介面、RESTful API、Docker 部署支援等功能。感謝原作者的卓越工作和開源貢獻！

### 🎯 核心特色

- 🤖 **多代理協作架構** - 專業化的 AI 代理團隊協同工作
- 📊 **全方位市場分析** - 整合技術面、基本面、情緒面、新聞面分析
- 🔄 **結構化決策流程** - 透過看漲/看跌辯論機制減少偏見
- 🧠 **長期記憶系統** - 使用 ChromaDB 向量數據庫儲存歷史決策
- 🎨 **現代化 Web 介面** - 基於 Next.js 16 的響應式 UI
- 🔌 **RESTful API** - 完整的後端 API 支援
- 🐳 **一鍵部署** - 支援 Docker Compose 和 Railway 部署
- 🔑 **BYOK (Bring Your Own Key)** - 使用者自帶 API 金鑰，保障隱私與成本控制

---

## 🏗️ 系統架構

TradingAgents 採用前後端分離架構，後端使用 FastAPI 提供 RESTful API，前端使用 Next.js 打造現代化的使用者介面。

### 📂 專案結構概覽

```
TradingAgents/
├── backend/                   # FastAPI 後端服務
│   ├── __main__.py           # 後端應用入口
│   ├── requirements.txt      # Python 依賴列表
│   └── app/
│       ├── main.py           # FastAPI 應用主程式
│       ├── api/              # API 路由層
│       │   ├── routes.py     # API 端點定義
│       │   └── dependencies.py  # 依賴注入
│       ├── core/             # 核心配置
│       │   ├── config.py     # 環境變數與設定
│       │   └── cors.py       # CORS 中間件配置
│       ├── models/           # 資料模型
│       │   └── schemas.py    # Pydantic 資料結構
│       └── services/         # 業務邏輯層
│           ├── trading_service.py  # TradingAgents 核心整合
│           └── price_service.py    # 股價資料處理服務
│
├── frontend/                  # Next.js 前端應用
│   ├── app/                  # Next.js App Router
│   │   ├── layout.tsx        # 根佈局組件
│   │   ├── page.tsx          # 首頁
│   │   └── analysis/         # 分析功能模組
│   │       ├── page.tsx      # 分析配置頁面
│   │       └── results/      # 分析結果展示頁面
│   ├── components/           # React 組件庫
│   │   ├── analysis/         # 分析相關組件
│   │   │   ├── AnalysisForm.tsx    # 參數配置表單
│   │   │   ├── TradingDecision.tsx # 交易決策卡片
│   │   │   ├── AnalystReport.tsx   # 分析師報告展示
│   │   │   └── PriceChart.tsx      # 股價圖表組件
│   │   ├── layout/           # 佈局組件
│   │   │   ├── Header.tsx    # 頂部導航欄
│   │   │   └── Footer.tsx    # 頁腳
│   │   ├── shared/           # 共用組件
│   │   └── ui/               # shadcn/ui 基礎組件
│   ├── context/              # React Context API
│   │   └── AnalysisContext.tsx  # 分析狀態管理
│   ├── hooks/                # 自定義 React Hooks
│   │   ├── useAnalysis.ts    # 分析請求管理
│   │   └── useConfig.ts      # 配置資料獲取
│   └── lib/                  # 工具函式庫
│       ├── api.ts            # API 客戶端封裝
│       ├── types.ts          # TypeScript 型別定義
│       └── utils.ts          # 通用輔助函式
│
└── tradingagents/            # 核心 Python 套件
    ├── agents/               # AI 代理定義
    ├── dataflows/            # 資料流處理
    ├── graph/                # LangGraph 工作流
    └── default_config.py     # 預設配置
```

### 🔧 後端技術棧

| 技術 | 用途 | 版本 |
|------|------|------|
| **FastAPI** | 現代化異步 Web 框架 | ≥0.104.0 |
| **Pydantic** | 資料驗證與序列化 | ≥2.9.0 |
| **LangGraph** | 多代理工作流編排引擎 | ≥0.4.8 |
| **LangChain** | LLM 應用開發框架 | Latest |
| **ChromaDB** | 向量資料庫（記憶系統） | ≥1.0.12 |
| **yfinance** | 股票市場資料獲取 | ≥0.2.63 |
| **Uvicorn** | ASGI 伺服器 | ≥0.24.0 |
| **python-dotenv** | 環境變數管理 | 1.0.0 |

#### 其他整合
- **stockstats**: 技術指標計算
- **feedparser**: RSS 新聞抓取
- **praw**: Reddit 社群情緒分析
- **finnhub-python**: 金融資料 API
- **beautifulsoup4**: 網頁內容解析

### 🎨 前端技術棧

| 技術 | 用途 | 版本 |
|------|------|------|
| **Next.js** | React 全端框架 | 16.x |
| **TypeScript** | 靜態型別檢查 | Latest |
| **Tailwind CSS** | 實用優先的 CSS 框架 | Latest |
| **shadcn/ui** | 可高度客製化的 UI 組件庫 | Latest |
| **React Hook Form** | 高效能表單管理 | Latest |
| **Zod** | TypeScript 優先的結構驗證 | Latest |
| **Recharts** | 資料視覺化圖表庫 | Latest |
| **Axios** | Promise 基礎的 HTTP 客戶端 | Latest |
| **react-markdown** | Markdown 內容渲染 | Latest |

---

## 🚀 快速開始

### 📋 前置要求

在開始之前，請確保您的系統已安裝以下軟體：

- **Python** 3.10 或更高版本
- **Node.js** 18.x 或更高版本
- **pnpm** 最新版本（推薦）或 npm
- **Conda** (可選，但強烈推薦用於 Python 環境管理)
- **Git** 用於克隆專案

#### 必要的 API 金鑰

- **OpenAI API Key** (必需) - 用於驅動 AI 代理
  - 申請網址: https://platform.openai.com/api-keys
- **Alpha Vantage API Key** (可選) - 用於更詳細的股票資料
  - 申請網址: https://www.alphavantage.co/support/#api-key

> 💡 **提示**: 本系統採用 BYOK (Bring Your Own Key) 模式，您可以在前端介面直接輸入 API 金鑰，無需設定環境變數（適合快速測試）。

### 📥 安裝步驟

#### 1️⃣ 克隆專案

```bash
git clone https://github.com/MarkLo127/TradingAgents.git
cd TradingAgents
```

#### 2️⃣ 後端設置

##### 2.1 創建 Python 虛擬環境

**使用 Conda (推薦)**
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

**或使用 venv**
```bash
python3 -m venv tradingagents
source tradingagents/bin/activate  # macOS/Linux
# 或
tradingagents\Scripts\activate  # Windows
```

##### 2.2 安裝 Python 依賴

```bash
# 安裝 TradingAgents 核心套件
pip install -e .

# 安裝後端 API 依賴
pip install -r backend/requirements.txt
```

##### 2.3 配置環境變數

複製範例環境變數檔案並編輯：

```bash
cp .env.example .env
```

編輯 `.env` 檔案，填入您的 API 金鑰：

```bash
# ============ API 金鑰配置 ============
# OpenAI API (必需)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Alpha Vantage API (可選)
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

# 其他 LLM 提供商 (可選)
ANTHROPIC_API_KEY=your-claude-api-key
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_API_KEY=your-gemini-api-key

# ============ 後端服務配置 ============
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# ============ CORS 配置 ============
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ============ 資料儲存配置 ============
TRADINGAGENTS_RESULTS_DIR=./results
```

##### 2.4 啟動後端服務

```bash
# 從專案根目錄執行
python -m backend
```

✅ 後端服務成功啟動後，您可以訪問：
- **應用根目錄**: http://localhost:8000
- **API 互動式文檔 (Swagger UI)**: http://localhost:8000/docs
- **API 文檔 (ReDoc)**: http://localhost:8000/redoc
- **健康檢查端點**: http://localhost:8000/api/health

#### 3️⃣ 前端設置

##### 3.1 安裝前端依賴

```bash
# 使用 pnpm (推薦)
pnpm -C frontend install

# 或使用 npm
npm --prefix frontend install
```

##### 3.2 配置前端環境變數 (可選)

如果您需要自訂 API 端點，可以建立 `frontend/.env.local`：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> 💡 預設情況下，前端會自動連接到 `http://localhost:8000`

##### 3.3 啟動前端開發伺服器

```bash
# 使用 pnpm (推薦)
pnpm -C frontend dev

# 或使用 npm
npm --prefix frontend run dev
```

✅ 前端應用成功啟動後，訪問：
- **應用首頁**: http://localhost:3000

---

## 🐳 部署方案

### Docker Compose 本地部署

最簡單的部署方式，一鍵啟動前後端服務：

```bash
# 啟動所有服務（首次執行會自動構建映像）
docker compose up -d --build

# 查看服務運行狀態
docker compose ps

# 查看即時日誌
docker compose logs -f

# 查看特定服務日誌
docker compose logs -f backend
docker compose logs -f frontend

# 停止服務
docker compose down

# 停止服務並清除資料卷
docker compose down -v
```

**Docker Compose 配置說明**：
- 後端服務運行於: `http://localhost:8000`
- 前端服務運行於: `http://localhost:3000`
- 分析結果會持久化儲存在 `./results` 目錄

---

## 📱 使用指南

### 基本工作流程

1. **訪問首頁** 
   - 開啟瀏覽器，訪問 http://localhost:3000
   - 查看系統介紹與功能說明

2. **進入分析頁面**
   - 點擊首頁的「開始分析」按鈕
   - 或直接訪問 http://localhost:3000/analysis

3. **配置分析參數**

   - **選擇分析師團隊**: 勾選您需要的分析師類型
     - ✅ 市場分析師 (Market Analyst) - 技術分析與價格走勢
     - ✅ 情緒分析師 (Sentiment Analyst) - 社交媒體情緒評估
     - ✅ 新聞分析師 (News Analyst) - 新聞事件影響分析
     - ✅ 基本面分析師 (Fundamental Analyst) - 財務數據與估值分析

   - **輸入股票代碼**: 例如 `NVDA`, `AAPL`, `TSLA`, `GOOGL`
     - 支援美股股票代號

   - **選擇分析日期**: 選擇要分析的特定日期
     - 預設為當前日期

   - **設定研究深度**:
     - 🟢 **淺層 (Shallow)**: 快速分析，適合即時決策
     - 🟡 **中等 (Medium)**: 平衡速度與深度
     - 🔴 **深層 (Deep)**: 全面深入分析，耗時較長

   - **選擇 LLM 模型**:
     
     系統提供兩種類型的模型配置：
     
     **快速思維模型** (用於快速分析和即時回應):
     - `gpt-5.1-2025-11-13` - GPT-5.1 (最新)
     - `gpt-5-mini-2025-08-07` - GPT-5 Mini (預設)
     - `gpt-5-nano-2025-08-07` - GPT-5 Nano
     - `gpt-4.1-mini` - GPT-4.1 Mini
     - `gpt-4.1-nano` - GPT-4.1 Nano
     - `o4-mini-2025-04-16` - o4-mini
     
     **深層思維模型** (用於複雜推理和深度分析):
     - `gpt-5.1-2025-11-13` - GPT-5.1 (最新)
     - `gpt-5-mini-2025-08-07` - GPT-5 Mini (預設)
     - `gpt-5-nano-2025-08-07` - GPT-5 Nano
     - `gpt-4.1-mini` - GPT-4.1 Mini
     - `gpt-4.1-nano` - GPT-4.1 Nano
     - `o4-mini-2025-04-16` - o4-mini
     
     > 💡 **提示**: 快速思維模型用於初步分析和資料收集，深層思維模型用於複雜決策和策略制定。您可以根據需求選擇不同的模型組合。

   - **輸入 API 金鑰**:
     - 在表單中直接輸入您的 OpenAI API Key
     - 或使用環境變數預設值（如已配置）

4. **執行分析**
   - 檢查所有參數無誤後，點擊「執行分析」按鈕
   - 系統會顯示載入動畫，處理時間依研究深度而定（1-5 分鐘）

5. **查看分析結果**
   - 分析完成後自動跳轉至結果頁面
   - 結果包含以下內容：

   **📊 交易決策摘要**
   - 最終決策: BUY / SELL / HOLD
   - 建議倉位大小
   - 風險等級評估
   - 核心理由總結

   **📈 股價走勢圖表**
   - 互動式價格圖表（支援折線圖/K線圖切換）
   - 交易量變化
   - 關鍵技術指標

   **📄 各分析師詳細報告**
   - 市場分析師: 技術面分析與趨勢判斷
   - 情緒分析師: 社群媒體情緒指標
   - 新聞分析師: 最新新聞事件影響評估
   - 基本面分析師: 財務健康度與估值分析
   - 研究團隊辯論: 看漲與看跌觀點對比
   - 交易員建議: 具體執行計畫
   - 風險管理: 風險因子與對策

### API 使用範例

如果您想要透過 API 整合 TradingAgents，可以參考以下範例：

#### 健康檢查

```bash
curl http://localhost:8000/api/health
```

#### 執行股票分析

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "NVDA",
    "analysis_date": "2024-01-15",
    "research_depth": "medium",
    "model": "gpt-5-mini-2025-08-07",
    "selected_analysts": ["market", "sentiment", "news", "fundamental"],
    "api_key": "sk-your-openai-key"
  }'
```

#### 獲取股價資料

```bash
curl "http://localhost:8000/api/price-data/NVDA?start_date=2024-01-01&end_date=2024-01-31"
```

完整的 API 文檔請訪問: http://localhost:8000/docs

---

## 🧠 核心功能詳解

### 多代理協作系統

TradingAgents 模擬真實交易公司的組織架構，每個代理都有其專業職責：

| 代理角色 | 主要職責 | 輸出內容 |
|---------|---------|---------|
| **市場分析師** | 技術分析 | 技術指標（RSI, MACD, 布林通道）、價格走勢、支撐阻力位 |
| **情緒分析師** | 情緒評估 | Reddit/Twitter 情緒指標、熱度趨勢、投資者信心指數 |
| **新聞分析師** | 新聞分析 | 最新新聞摘要、事件影響評估、市場反應預測 |
| **基本面分析師** | 財務分析 | 財報數據、估值指標（P/E, P/B）、盈利能力評估 |
| **看漲研究員** | 多頭論證 | 看漲理由、上漲催化劑、目標價位 |
| **看跌研究員** | 空頭論證 | 看跌理由、下跌風險、防守策略 |
| **交易員** | 決策整合 | 綜合所有報告，制定交易計劃 |
| **風險管理** | 風險控制 | 風險評估、倉位建議、止損止盈設定 |
| **投資組合經理** | 最終決策 | 最終交易決定（批准/拒絕），執行指令 |

### 工作流程圖

```
┌─────────────────┐
│  使用者輸入參數   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  資料收集階段    │ ◄── yfinance, Reddit, RSS
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│     分析師團隊平行分析        │
│  ┌────┬────┬────┬────────┐ │
│  │市場│情緒│新聞│基本面│ │
│  └────┴────┴────┴────────┘ │
└────────┬─────────────────────┘
         │
         ▼
┌─────────────────┐
│  研究團隊辯論    │
│  看漲 vs 看跌   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  交易員整合分析  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  風險管理評估    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 投資組合經理決策 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  輸出最終報告    │
└─────────────────┘
```

### 智能特性

#### 1. 動態研究深度調整
- **Shallow**: 每個代理進行 1 輪分析，適合快速決策
- **Medium**: 每個代理進行 2-3 輪分析，平衡深度與速度
- **Deep**: 每個代理進行 5+ 輪分析，全面深入研究

#### 2. 多模型支持
- 支援 OpenAI (GPT-4, GPT-4o, o1 系列)
- 支援 Anthropic Claude
- 支援 Google Gemini
- 支援 Google Gemini

#### 3. 長期記憶系統
- 使用 ChromaDB 向量資料庫儲存歷史決策
- 代理可以參考過去類似情況的決策
- 持續學習與改進分析品質

#### 4. 結構化輸出
- 所有報告均採用 Markdown 格式
- 清晰的章節結構
- 支援表格、列表、程式碼區塊等豐富格式

#### 5. 實時資料整合
- yfinance: 即時股價與歷史資料
- Reddit API: 社群情緒分析
- RSS Feeds: 財經新聞抓取
- Alpha Vantage: 詳細財務資料（可選）

---

## 📸 應用截圖

### 首頁 - 功能介紹

展示系統的核心功能與運作流程

![首頁](web_screenshot/1.png)

### 分析配置頁面

直觀的表單介面，輕鬆配置所有分析參數

![分析配置頁面](web_screenshot/2.png)

### 股價走勢與交易量（折線圖）

互動式圖表展示股價變化與交易量

![股價走勢與交易量（折線圖）](web_screenshot/3.png)

### 股價走勢與交易量（K線圖）

專業的 K 線圖視覺化，適合技術分析

![股價走勢與交易量（K線圖）](web_screenshot/4.png)

### 市場分析師報告

詳細的技術面分析與市場趨勢判斷

![市場分析師報告](web_screenshot/5.png)

### 情緒分析師報告

社群媒體情緒指標與投資者信心評估

![情緒分析師報告](web_screenshot/6.png)

### 新聞分析師報告

最新財經新聞摘要與事件影響分析

![新聞分析師報告](web_screenshot/7.png)

### 基本面分析師報告

財務數據解析與價值評估

![基本面分析師報告](web_screenshot/8.png)

---

## 🙏 致謝

### 特別感謝

本專案基於 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 的原始專案進行改進和擴展。衷心感謝原作者創建了如此優秀的多代理交易分析框架，為我們提供了堅實的基礎。

### 使用的開源專案

本專案使用了以下優秀的開源專案：

- [LangChain](https://github.com/langchain-ai/langchain) - LLM 應用開發框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 多代理工作流編排
- [FastAPI](https://github.com/tiangolo/fastapi) - 現代化 Python Web 框架
- [Next.js](https://github.com/vercel/next.js) - React 全端框架
- [shadcn/ui](https://github.com/shadcn/ui) - 精美的 React 組件庫
- [ChromaDB](https://github.com/chroma-core/chroma) - AI 原生向量資料庫
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance 資料下載工具
