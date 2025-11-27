#!/bin/bash

# ========================================
# 清理開發與構建緩存腳本
# 此腳本會清理 pnpm 和開發過程中產生的緩存文件
# 不會影響項目的源代碼和依賴包
# ========================================

set -e  # 遇到錯誤立即停止

echo "🧹 開始清理緩存..."
echo "================================"

# 記錄腳本執行位置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ========================================
# 前端緩存清理
# ========================================
echo ""
echo "📦 清理前端緩存..."

if [ -d "frontend/.next" ]; then
    echo "  ✓ 刪除 frontend/.next (Next.js 構建輸出)"
    rm -rf frontend/.next
else
    echo "  - frontend/.next 不存在，跳過"
fi

if [ -d "frontend/.turbo" ]; then
    echo "  ✓ 刪除 frontend/.turbo (Turbopack 緩存)"
    rm -rf frontend/.turbo
else
    echo "  - frontend/.turbo 不存在，跳過"
fi

if [ -d "frontend/out" ]; then
    echo "  ✓ 刪除 frontend/out (靜態導出輸出)"
    rm -rf frontend/out
else
    echo "  - frontend/out 不存在，跳過"
fi

# 清理 TypeScript 增量編譯緩存
if [ -f "frontend/tsconfig.tsbuildinfo" ]; then
    echo "  ✓ 刪除 frontend/tsconfig.tsbuildinfo (TS 增量緩存)"
    rm -f frontend/tsconfig.tsbuildinfo
else
    echo "  - TypeScript 緩存不存在，跳過"
fi

# ========================================
# 後端緩存清理
# ========================================
echo ""
echo "🐍 清理後端緩存..."

# 清理 Python 緩存
PYCACHE_COUNT=$(find backend -type d -name "__pycache__" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    echo "  ✓ 刪除 $PYCACHE_COUNT 個 __pycache__ 目錄"
    find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
else
    echo "  - 沒有 __pycache__ 目錄，跳過"
fi

# 清理 .pyc 文件
PYC_COUNT=$(find backend -type f -name "*.pyc" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYC_COUNT" -gt 0 ]; then
    echo "  ✓ 刪除 $PYC_COUNT 個 .pyc 文件"
    find backend -type f -name "*.pyc" -delete 2>/dev/null || true
else
    echo "  - 沒有 .pyc 文件，跳過"
fi

# 清理 .pyo 文件
PYO_COUNT=$(find backend -type f -name "*.pyo" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYO_COUNT" -gt 0 ]; then
    echo "  ✓ 刪除 $PYO_COUNT 個 .pyo 文件"
    find backend -type f -name "*.pyo" -delete 2>/dev/null || true
else
    echo "  - 沒有 .pyo 文件，跳過"
fi

# 清理 pytest 緩存
if [ -d "backend/.pytest_cache" ]; then
    echo "  ✓ 刪除 backend/.pytest_cache (Pytest 緩存)"
    rm -rf backend/.pytest_cache
else
    echo "  - Pytest 緩存不存在，跳過"
fi

# ========================================
# 通用緩存清理
# ========================================
echo ""
echo "🔧 清理通用緩存..."

# 清理 macOS 系統文件
DS_STORE_COUNT=$(find . -name ".DS_Store" 2>/dev/null | wc -l | tr -d ' ')
if [ "$DS_STORE_COUNT" -gt 0 ]; then
    echo "  ✓ 刪除 $DS_STORE_COUNT 個 .DS_Store 文件 (macOS 緩存)"
    find . -name ".DS_Store" -delete 2>/dev/null || true
else
    echo "  - 沒有 .DS_Store 文件，跳過"
fi

# 清理日誌文件
if [ -f "npm-debug.log" ]; then
    echo "  ✓ 刪除 npm-debug.log"
    rm -f npm-debug.log
fi

if [ -f "yarn-error.log" ]; then
    echo "  ✓ 刪除 yarn-error.log"
    rm -f yarn-error.log
fi

# ========================================
# 計算清理的空間
# ========================================
echo ""
echo "================================"
echo "✅ 清理完成！"
echo ""
echo "📋 保留的重要文件："
echo "  ✓ node_modules (依賴包)"
echo "  ✓ pnpm-lock.yaml (鎖定文件)"
echo "  ✓ package.json (包配置)"
echo "  ✓ 所有源代碼文件"
echo ""
echo "💡 提示："
echo "  - 下次運行 'pnpm dev' 時，緩存會自動重新生成"
echo "  - 如果需要重新安裝依賴，請運行 'pnpm install'"
echo ""
