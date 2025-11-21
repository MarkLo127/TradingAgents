# TradingAgents 雲端部署指南 🚀

本指南提供將 TradingAgents 部署到雲端的完整步驟，**重點介紹完全免費的部署方案**。

## 📋 目錄

- [免費部署方案（推薦）](#免費部署方案推薦)
- [部署前準備](#部署前準備)
- [方案 1: Vercel + Render (完全免費)](#方案-1-vercel--render-完全免費)
- [方案 2: Railway (免費額度)](#方案-2-railway-免費額度)
- [方案 3: Docker Compose (自有伺服器)](#方案-3-docker-compose-自有伺服器)
- [環境變數配置](#環境變數配置)
- [故障排除](#故障排除)

---

## 🎯 免費部署方案（推薦）

### 最佳免費組合：Vercel (Frontend) + Render (Backend)

| 服務 | 平台 | 免費額度 | 限制 |
|------|------|----------|------|
| **Frontend** | Vercel | 無限制 | 100GB 頻寬/月 |
| **Backend** | Render | 750 小時/月 | 休眠機制（15分鐘無活動） |

> [!TIP]
> Render 的免費方案會在 15 分鐘無活動後休眠，首次訪問需要 30-60 秒喚醒。這對於測試和個人使用完全足夠！

---

## 🔧 部署前準備

### 1. 必要的 API 密鑰

您需要準備以下 API 密鑰：

#### OpenAI API Key（必需）
- 註冊：https://platform.openai.com/
- 獲取 API Key：https://platform.openai.com/api-keys
- 費用：按使用量計費（建議使用 gpt-4o-mini 節省成本）

#### Alpha Vantage API Key（必需）
- 註冊：https://www.alphavantage.co/support/#api-key
- **完全免費**，TradingAgents 用戶享有 60 請求/分鐘

### 2. GitHub 帳號
所有免費部署方案都需要 GitHub 帳號來連接代碼倉庫。

---

## 🎨 方案 1: Vercel + Render (完全免費)

這是**最推薦的免費方案**，前端和後端分別部署。

### Step 1: 部署 Backend 到 Render

#### 1.1 準備代碼
確保您的代碼已推送到 GitHub。

#### 1.2 創建 Render 帳號
訪問 https://render.com/ 並使用 GitHub 登入。

#### 1.3 創建新的 Web Service

1. 點擊 "New +" → "Web Service"
2. 連接您的 GitHub 倉庫
3. 配置如下：

```
Name: tradingagents-backend
Region: Singapore (或最近的區域)
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 1.4 設置環境變數

在 Render 的 Environment 頁面添加：

```bash
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
TRADINGAGENTS_RESULTS_DIR=/opt/render/project/src/results
PYTHON_VERSION=3.11.9
```

> [!IMPORTANT]
> Render 要求 `PYTHON_VERSION` 必須是完整的版本號（例如 `3.11.9`），不能只是 `3.11`。

#### 1.5 選擇免費方案
- Instance Type: **Free**
- 點擊 "Create Web Service"

部署需要 5-10 分鐘。完成後，您會獲得一個 URL，例如：
```
https://tradingagents-backend.onrender.com
```

### Step 2: 部署 Frontend 到 Vercel

#### 2.1 創建 Vercel 帳號
訪問 https://vercel.com/ 並使用 GitHub 登入。

#### 2.2 導入項目

1. 點擊 "Add New..." → "Project"
2. 選擇您的 GitHub 倉庫
3. 配置如下：

```
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

#### 2.3 設置環境變數

在 Environment Variables 添加：

```bash
NEXT_PUBLIC_API_URL=https://tradingagents-backend.onrender.com
```

> [!IMPORTANT]
> 將 `tradingagents-backend.onrender.com` 替換為您在 Step 1 獲得的實際 Render URL。

#### 2.4 部署

點擊 "Deploy"，等待 2-3 分鐘。完成後，您會獲得一個 URL，例如：
```
https://tradingagents.vercel.app
```

### Step 3: 更新 Backend CORS 設置

為了讓前端能夠訪問後端，需要更新 Backend 的 CORS 配置。

編輯 `backend/app/main.py`，找到 CORS 配置部分，添加您的 Vercel URL：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://tradingagents.vercel.app",  # 添加您的 Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

提交並推送更改，Render 會自動重新部署。

### ✅ 完成！

訪問您的 Vercel URL，應用程式現在已經在線上運行了！

---

## 🚂 方案 2: Railway (免費額度)

Railway 提供 $5 免費額度/月，可以同時部署前後端。

### Step 1: 創建 Railway 帳號
訪問 https://railway.app/ 並使用 GitHub 登入。

### Step 2: 創建新項目

1. 點擊 "New Project"
2. 選擇 "Deploy from GitHub repo"
3. 選擇您的倉庫

### Step 3: 添加服務

#### 3.1 添加 Backend 服務

1. 點擊 "New Service" → "GitHub Repo"
2. 配置：
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. 添加環境變數：
```bash
OPENAI_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
TRADINGAGENTS_RESULTS_DIR=/app/results
```

4. 在 Settings → Networking 中生成一個公開域名

#### 3.2 添加 Frontend 服務

1. 點擊 "New Service" → "GitHub Repo"
2. 配置：
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`

3. 添加環境變數：
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

4. 在 Settings → Networking 中生成一個公開域名

### ✅ 完成！

兩個服務都會自動部署，您可以通過生成的域名訪問。

> [!WARNING]
> Railway 免費額度為 $5/月，通常可以運行約 500 小時。超出後需要付費。

---

## 🐳 方案 3: Docker Compose (自有伺服器)

如果您有自己的 VPS（如 DigitalOcean、Linode、AWS EC2 等），可以使用 Docker Compose。

### 前置要求
- 安裝 Docker 和 Docker Compose
- 至少 2GB RAM
- 開放端口 80 和 443

### Step 1: 準備環境變數

創建 `.env` 文件：

```bash
cp .env.example .env
```

編輯 `.env`，填入您的 API 密鑰：

```bash
OPENAI_API_KEY=your_openai_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
TRADINGAGENTS_RESULTS_DIR=/app/results
```

### Step 2: 修改 docker-compose.yml

確保 frontend 的環境變數指向正確的後端 URL：

```yaml
environment:
  - NEXT_PUBLIC_API_URL=http://your-server-ip:8000
```

### Step 3: 構建並啟動

```bash
# 構建鏡像
docker-compose build

# 啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

### Step 4: 訪問應用

- Frontend: http://your-server-ip:3000
- Backend API: http://your-server-ip:8000

### 使用 Nginx 反向代理（可選）

為了使用域名和 HTTPS，可以配置 Nginx：

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

使用 Certbot 獲取免費 SSL 證書：

```bash
sudo certbot --nginx -d yourdomain.com
```

---

## 🔐 環境變數配置

### Backend 環境變數

| 變數名 | 必需 | 說明 | 範例 |
|--------|------|------|------|
| `OPENAI_API_KEY` | ✅ | OpenAI API 密鑰 | `sk-...` |
| `ALPHA_VANTAGE_API_KEY` | ✅ | Alpha Vantage API 密鑰 | `YOUR_KEY` |
| `TRADINGAGENTS_RESULTS_DIR` | ⚠️ | 結果存儲目錄 | `/app/results` |
| `PYTHON_VERSION` | ❌ | Python 版本（Render） | `3.11` |

### Frontend 環境變數

| 變數名 | 必需 | 說明 | 範例 |
|--------|------|------|------|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend API URL | `https://api.yourdomain.com` |

> [!CAUTION]
> 永遠不要在前端代碼中硬編碼 API 密鑰！所有敏感信息應該在後端處理。

---

## 🔧 故障排除

### Backend 問題

#### 問題：Render 服務休眠
**症狀**：首次訪問需要等待 30-60 秒

**解決方案**：
- 這是 Render 免費方案的正常行為
- 可以使用 UptimeRobot 等服務定期 ping 您的 API 保持喚醒
- 或升級到付費方案（$7/月）

#### 問題：ModuleNotFoundError
**症狀**：找不到 `tradingagents` 模組

**解決方案**：
確保 `backend/Dockerfile` 正確複製了 tradingagents 目錄：
```dockerfile
COPY ../tradingagents ./tradingagents
```

#### 問題：API 速率限制
**症狀**：Alpha Vantage 返回 429 錯誤

**解決方案**：
- 確認使用的是 TradingAgents 專用 API key（60 req/min）
- 或在 `tradingagents/default_config.py` 中切換到其他數據源

### Frontend 問題

#### 問題：CORS 錯誤
**症狀**：瀏覽器控制台顯示 CORS 錯誤

**解決方案**：
在 `backend/app/main.py` 中添加您的前端 URL 到 CORS 白名單：
```python
allow_origins=[
    "https://your-frontend-url.vercel.app",
]
```

#### 問題：API 連接失敗
**症狀**：前端無法連接到後端

**解決方案**：
1. 檢查 `NEXT_PUBLIC_API_URL` 環境變數是否正確
2. 確保後端服務正在運行
3. 檢查後端 URL 是否可以公開訪問

### Docker 問題

#### 問題：構建失敗
**症狀**：`docker-compose build` 失敗

**解決方案**：
```bash
# 清理舊的鏡像和緩存
docker-compose down -v
docker system prune -a

# 重新構建
docker-compose build --no-cache
```

#### 問題：容器無法啟動
**症狀**：`docker-compose up` 後容器立即退出

**解決方案**：
```bash
# 查看詳細日誌
docker-compose logs backend
docker-compose logs frontend

# 檢查環境變數
docker-compose config
```

---

## 🔑 Bring Your Own Key (BYOK) 模式

如果您希望讓用戶使用自己的 API Key，而不是在服務器端配置：

1. **Render 配置**：
   - 不要設置 `OPENAI_API_KEY` 和 `ALPHA_VANTAGE_API_KEY` 環境變數
   - 或者將它們設置為空值

2. **前端行為**：
   - 應用程式會檢測到沒有預設 Key
   - 用戶在執行分析時，界面會要求輸入他們自己的 API Key
   - Key 僅用於當次請求，不會存儲在服務器上

這對於公開演示或讓社群使用您的部署版本非常有用，您無需為他人的使用付費。

---

## 📊 成本估算

### 完全免費方案（Vercel + Render）

| 項目 | 成本 |
|------|------|
| Frontend (Vercel) | **$0** |
| Backend (Render) | **$0** |
| Alpha Vantage API | **$0** |
| OpenAI API | 按使用量（建議使用 gpt-4o-mini） |

**預估 OpenAI 成本**：
- 使用 `gpt-4o-mini`：約 $0.01-0.05 每次交易分析
- 每天 10 次分析：約 $3-15/月

### Railway 方案

| 項目 | 成本 |
|------|------|
| Railway 免費額度 | $5/月（免費） |
| 超出後 | $0.000231/GB-s |
| OpenAI API | 按使用量 |

---

## 🎯 推薦配置

### 個人測試使用
- **平台**：Vercel + Render（免費）
- **LLM**：gpt-4o-mini（節省成本）
- **配置**：
```python
config["deep_think_llm"] = "gpt-4o-mini"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1
```

### 生產環境
- **平台**：Vercel + Railway（或 Render 付費方案）
- **LLM**：gpt-4o 或 o1-preview
- **配置**：使用默認配置
- **監控**：添加 Sentry 或 LogRocket

---

## 📚 相關資源

- [Vercel 文檔](https://vercel.com/docs)
- [Render 文檔](https://render.com/docs)
- [Railway 文檔](https://docs.railway.app/)
- [TradingAgents GitHub](https://github.com/TauricResearch/TradingAgents)
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)

---

## 🤝 需要幫助？

如果遇到問題：
1. 查看上面的[故障排除](#故障排除)部分
2. 檢查 GitHub Issues
3. 加入 [Discord 社群](https://discord.com/invite/hk9PGKShPK)

---

**祝您部署順利！** 🚀
