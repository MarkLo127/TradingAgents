#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試找出哪個字符在 STSong-Light 中被渲染為「煉」
"""
import sys
sys.path.insert(0, '/Users/yaolo/Desktop/TradingAgentsX')

from backend.app.services.pdf_generator import PDFGenerator
import io

# 測試內容 - 包含我們使用的所有符號
test_symbols = {
    '星號': '★',
    '菱形': '◆',
    '方塊': '▓',
    '小方': '▪',
    '雙菱': '◈',
    '空菱': '◇',
    '雙圓': '◎',
    '米字': '※',
    '時鐘': '◷',
    '點': '‧',
    '無限': '∞',
    '粗方': '▣',
    '對號': '✓',
    '叉號': '✗',
    '警告': '⚠',
    '閃電': '⚡',
}

print("測試每個符號在 PDF 中的渲染...\n")

pdf_gen = PDFGenerator()

for name, symbol in test_symbols.items():
    test_content = f"測試{name}符號: {symbol}"
    
    try:
        pdf_bytes = pdf_gen.generate_analyst_report_pdf(
            analyst_name=f"測試: {symbol}",
            ticker="TEST",
            analysis_date="2025-11-27",
            report_content=test_content
        )
        
        # 保存測試 PDF
        filename = f"/tmp/test_symbol_{name}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✓ {name} ({symbol}) - U+{ord(symbol):04X} - 已生成: {filename}")
    except Exception as e:
        print(f"✗ {name} ({symbol}) - 錯誤: {e}")

print("\n請手動檢查 /tmp/test_symbol_*.pdf 文件，看看哪個符號顯示為「煉」")
