# Railway 部署指南

您的專案已經配置好支援 **Railway (線上)** 和 **Docker (本地)** 雙重部署。兩者共用程式碼，但使用不同的設定檔。

## 1. 部署架構
- **本地 (Docker)**: 使用 `docker-compose.yml`，自動配置網絡和環境變數。
- **線上 (Railway)**: 使用 `railway.toml` 定義服務構建方式，但**需要您手動設定環境變數**。

## 2. Railway 環境變數設定 (必填)

在 Railway 的專案 Dashboard 中，請為各個服務設定以下變數：

### Backend 服務
| 變數名稱 | 值 / 說明 |
|---|---|
| `TRADINGAGENTS_RESULTS_DIR` | `/app/results` (建議值) |
| `TRADINGAGENTS_DATA_CACHE_DIR` | `/app/results/data_cache` (確保數據可寫入) |
| `PORT` | Railway 會自動注入，通常不需要手動設。 |
| `OPENAI_API_KEY` | **(BYOK 模式請勿設定)** 若您希望使用者使用自己的 Key，請不要在此設定。 |
| `ALPHA_VANTAGE_API_KEY` | **(BYOK 模式請勿設定)** 同上。 |

> **注意**: 
> 1. **BYOK 模式**: 若不設定 API Key，使用者在前端網頁**必須**自行輸入 Key 才能進行分析，否則會報錯。這適合公開分享。
> 2. **數據持久化**: Railway 的檔案系統是短暫的。若需持久化數據，請在 Railway 服務設定中掛載 **Volume** 到 `/app/results`。

### Frontend 服務
| 變數名稱 | 值 / 說明 |
|---|---|
| `BACKEND_URL` | `https://<您的-backend-服務網域>.up.railway.app` (填入 Backend 的公開網址) |
| `NEXT_PUBLIC_API_URL` | (留空或不設定) |

## 3. 部署步驟
1.  將程式碼推送到 GitHub。
2.  在 Railway 新增專案 -> "Deploy from GitHub repo"。
3.  Railway 會自動檢測 `railway.toml` 並建立 Backend 和 Frontend 兩個服務。
4.  **在服務啟動前** (或啟動失敗後)，進入 "Variables" 分頁設定上述變數。
5.  設定完成後，Railway 會自動重新部署。

## 4. 常見問題
- **Frontend 404**: 檢查 Frontend 的 `BACKEND_URL` 是否正確指向 Backend 的公開網址 (需包含 `https://`)。
- **Backend 401**: 檢查 Backend 的 `OPENAI_API_KEY` 是否正確。
- **Backend 500 (Permission Denied)**: 確保已設定 `TRADINGAGENTS_DATA_CACHE_DIR=/app/results/data_cache` 並且 (選用) 掛載了 Volume。
