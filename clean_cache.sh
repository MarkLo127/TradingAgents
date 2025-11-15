#!/usr/bin/env bash
set -e

# 預設清理當前目錄，也可以傳入指定目錄
TARGET_DIR="${1:-.}"

echo "🧹 Cleaning __pycache__ & .DS_Store under: $TARGET_DIR"

# 刪除所有 __pycache__ 資料夾
find "$TARGET_DIR" -type d -name "__pycache__" -exec rm -rf {} +

# 刪除所有 .DS_Store 檔案
find "$TARGET_DIR" -type f -name ".DS_Store" -delete

echo "✅ Done. All __pycache__ and .DS_Store removed."
