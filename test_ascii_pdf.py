#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/Users/yaolo/Desktop/TradingAgentsX')

from backend.app.services.pdf_generator import PDFGenerator

# 測試包含各種符號的內容
test_content = '''# 測試報告

## 市場分析
- 上漲趨勢 ^
- 技術指標 *
- 支撐位 o

## 風險評估
- 警告標記 [!]
- 確認標記 [OK]
- 否定標記 [X]

## 結論
純文字和 ASCII 符號測試，不應該出現「煉」字
'''

pdf_gen = PDFGenerator()
pdf_bytes = pdf_gen.generate_analyst_report_pdf(
    analyst_name='ASCII 符號測試',
    ticker='TEST',
    analysis_date='2025-11-27',
    report_content=test_content
)

with open('/tmp/test_ascii_only.pdf', 'wb') as f:
    f.write(pdf_bytes)

print('✓ 已生成測試 PDF: /tmp/test_ascii_only.pdf')
print('請檢查 PDF 中是否還有「煉」字出現')
print('如果沒有「煉」，說明 ASCII-only 方案成功解決問題')
