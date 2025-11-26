#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量禁用所有 agents 的 emoji 輸出
"""
import os
import re

# 定義需要修改的文件列表
AGENT_FILES = [
    # Analysts
    "tradingagents/agents/analysts/fundamentals_analyst.py",
    "tradingagents/agents/analysts/market_analyst.py",
    "trading agents/agents/analysts/news_analyst.py",
    "tradingagents/agents/analysts/social_media_analyst.py",
    # Researchers
    "tradingagents/agents/researchers/bear_researcher.py",
    "tradingagents/agents/researchers/bull_researcher.py",
    # Managers
    "tradingagents/agents/managers/research_manager.py",
    "tradingagents/agents/managers/risk_manager.py",
    # Trader
    "tradingagents/agents/trader/trader.py",
    # Risk Management
    "tradingagents/agents/risk_mgmt/aggresive_debator.py",
    "tradingagents/agents/risk_mgmt/conservative_debator.py",
    "tradingagents/agents/risk_mgmt/neutral_debator.py",
]

# 新的禁用 emoji 指令
NO_EMOJI_INSTRUCTION = """**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**
**嚴格禁止：請勿在回覆中使用任何 emoji 表情符號（如 ✅ ❌ 📊 📈 🚀 等）。**
**請只使用純文字、數字、標點符號和必要的 Unicode 符號（如 ↑ ↓ ★ ●等）。**"""

OLD_INSTRUCTION = """**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**"""

def update_agent_file(filepath):
    """更新單個 agent 文件"""
    full_path = filepath
    
    if not os.path.exists(full_path):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替換舊的指令為新的（包含禁用 emoji）
        if OLD_INSTRUCTION in content:
            new_content = content.replace(OLD_INSTRUCTION, NO_EMOJI_INSTRUCTION)
            
            # 寫回文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已更新: {filepath}")
            return True
        else:
            print(f"⚠️  未找到需要替換的內容: {filepath}")
            return False
    
    except Exception as e:
        print(f"❌ 錯誤: {filepath} - {str(e)}")
        return False

def main():
    """主函數"""
    print("開始批量禁用 agents 的 emoji 輸出...\n")
    
    success_count = 0
    total_count = len(AGENT_FILES)
    
    for agent_file in AGENT_FILES:
        if update_agent_file(agent_file):
            success_count += 1
    
    print(f"\n完成！成功更新 {success_count}/{total_count} 個文件")

if __name__ == "__main__":
    main()
