# TradingAgents - 多代理交易分析系統

> 基於 LangGraph 的智能股票交易分析平台，結合多個 AI 代理進行協作決策

- GitHub: [MarkLo127/TradingAgents](https://github.com/MarkLo127/TradingAgents)

## 系統架構

### 後端架構 (FastAPI)

```
backend/
├── __main__.py          # 應用入口點
├── requirements.txt     # Python 依賴
└── app/
    ├── main.py         # FastAPI 應用主程式
    ├── api/            # API 路由層
    │   ├── routes.py   # 分析、配置等 API 端點
    │   └── dependencies.py  # 依賴注入
    ├── core/           # 核心配置
    │   ├── config.py   # 環境變數設定
    │   └── cors.py     # CORS 配置
    ├── models/         # 數據模型
    │   └── schemas.py  # Pydantic 數據模式
    └── services/       # 業務邏輯
        ├── trading_service.py  # TradingAgents 整合
        └── price_service.py    # 股價數據處理
```

**核心技術棧**：
- **FastAPI**: 現代化異步 Web 框架
- **Pydantic**: 數據驗證與序列化
- **LangGraph**: 多代理工作流編排
- **LangChain**: LLM 整合框架
- **Chromadb**: 向量數據庫（記憶系統）
- **yfinance**: 股票數據獲取

### 前端架構 (Next.js)

```
frontend/
├── app/                # Next.js 應用路由
│   ├── layout.tsx     # 根佈局
│   ├── page.tsx       # 首頁
│   └── analysis/      # 分析功能
│       ├── page.tsx   # 分析表單頁面
│       └── results/   # 結果展示頁面
├── components/         # React 組件
│   ├── analysis/      # 分析相關組件
│   │   ├── AnalysisForm.tsx    # 分析參數表單
│   │   ├── TradingDecision.tsx # 交易決策展示
│   │   ├── AnalystReport.tsx   # 分析師報告
│   │   └── PriceChart.tsx      # 股價圖表
│   ├── layout/        # 佈局組件
│   │   ├── Header.tsx # 導航欄
│   │   └── Footer.tsx # 頁腳
│   ├── shared/        # 共用組件
│   └── ui/            # shadcn/ui 基礎組件
├── context/           # React Context
│   └── AnalysisContext.tsx  # 分析結果共享
├── hooks/             # 自定義 Hooks
│   ├── useAnalysis.ts # 分析請求管理
│   └── useConfig.ts   # 配置獲取
└── lib/               # 工具函數
    ├── api.ts         # API 客戶端
    ├── types.ts       # TypeScript 類型
    └── utils.ts       # 輔助函數
```

**核心技術棧**：
- **Next.js 16**: React 全棧框架
- **TypeScript**: 靜態類型檢查
- **Tailwind CSS**: 實用優先的 CSS 框架
- **shadcn/ui**: 可定制的 UI 組件庫
- **React Hook Form + Zod**: 表單驗證
- **Recharts**: 數據可視化
- **Axios**: HTTP 客戶端
- **react-markdown**: Markdown 渲染

## 安裝步驟

### 前置要求

- **Python**: 3.10 或以上
- **Node.js**: 18.x 或以上
- **pnpm**: 最新版本
- **Conda**: (推薦) 用於 Python 環境管理
- **API 金鑰**:
  - OpenAI API Key (必需)
  - Alpha Vantage API Key (可選，用於更詳細數據)

### 1. 克隆專案

```bash
git clone https://github.com/MarkLo127/TradingAgents.git
cd TradingAgents
```

### 2. 後端設置

#### 2.1 創建 Python 環境

```bash
# 使用 Conda (推薦)
conda create -n tradingagents python=3.13
conda activate tradingagents
```

#### 2.2 安裝依賴

```bash
# 安裝 TradingAgents 核心
pip install -e .

# 安裝後端依賴
pip install -r backend/requirements.txt
```

#### 2.3 環境配置

在專案根目錄創建 `.env` 文件：

```bash
# API 金鑰
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key  # 可選

# 後端配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### 2.4 啟動後端

```bash
# 從專案根目錄運行
python -m backend
```

後端將運行在 `http://localhost:8000`

- API 文檔: http://localhost:8000/docs
- 健康檢查: http://localhost:8000/api/health

### 3. 前端設置

#### 3.1 安裝依賴

```bash
pnpm -C frontend i
```

#### 3.2 啟動前端

```bash
pnpm -C frontend dev
```

前端將運行在 `http://localhost:3000`

### Docker 部署

```bash
# 使用 Docker Compose 啟動
docker compose up -d --build

# 查看日誌
docker compose logs -f

# 停止服務
docker compose down -v
```

### 使用流程

1. **訪問首頁** - 查看功能介紹
2. **進入分析頁面** - 點擊"開始分析"
3. **配置參數**：
   - 選擇分析師團隊（市場、情緒、新聞、基本面）
   - 輸入股票代碼（如 NVDA, AAPL, TSLA）
   - 選擇分析日期
   - 設定研究深度（淺層/中等/深層）
   - 選擇 LLM 模型
   - 輸入 API 金鑰
4. **執行分析** - 點擊"執行分析"按鈕
5. **查看結果** - 自動跳轉至結果頁面，查看：
   - 交易決策（買入/賣出/持有）
   - 股價走勢圖表
   - 各分析師詳細報告

## 核心功能

### 多代理協作系統

- **市場分析師**: 技術指標與價格走勢分析
- **情緒分析師**: 社交媒體情緒分析
- **新聞分析師**: 新聞事件影響評估  
- **基本面分析師**: 財務數據與估值分析
- **研究團隊**: 看漲/看跌辯論機制
- **交易員**: 投資計劃制定
- **風險管理**: 風險評估與倉位管理

### 智能特性

- **動態研究深度**: 可調節分析詳細程度
- **多模型支持**: GPT-4o, GPT-5.1 等
- **記憶系統**: ChromaDB 向量存儲歷史決策
- **Markdown 報告**: 格式化的分析輸出
- **實時數據**: yfinance 股票數據整合

## 應用截圖

### 首頁

![首頁](web_screenshot/1.png)

### 分析配置頁面

![分析配置](web_screenshot/2.png)

### 股價走勢與交易量（折線圖）

![股價走勢與交易量（折線圖）](web_screenshot/3.png)

### 股價走勢與交易量（K線圖）

![股價走勢與交易量（K線圖）](web_screenshot/4.png)

### 市場分析師報告

![市場分析師報告](web_screenshot/5.png)

### 社群分析師報告

![社群分析師報告](web_screenshot/6.png)

### 新聞分析師報告

![新聞分析師報告](web_screenshot/7.png)

### 基本面 分析師報告

![基本面分析師報告](web_screenshot/8.png)
