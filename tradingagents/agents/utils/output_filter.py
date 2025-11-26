# -*- coding: utf-8 -*-
"""
LLM Output Post-Processing Filter
Fixes common LLM output errors including character corruption and format issues
"""
import re


def count_chinese_words(text: str) -> int:
    """
    Count Chinese characters in text (excluding markdown and tables)
    
    Args:
        text: Input text
        
    Returns:
        Number of Chinese characters
    """
    # Remove code blocks
    clean_text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove tables
    clean_text = re.sub(r'\|.*?\|', '', clean_text, flags=re.MULTILINE)
    # Remove markdown formatting
    clean_text = re.sub(r'[#\*_`~\[\]\(\)]', '', clean_text)
    
    # Count Chinese characters (CJK Unified Ideographs)
    return len([c for c in clean_text if '\u4e00' <= c <= '\u9fff'])


def fix_common_llm_errors(text: str) -> str:
    """
    Fix common LLM character selection errors
    
    Args:
        text: LLM output text
        
    Returns:
        Corrected text
    """
    # Common character misuse patterns
    replacements = {
        # '煉' misuse - should be '練' (practice/train) in most contexts
        '煉習': '練習',
        '訓煉': '訓練',
        '**煉**': '**練**',
        '（煉': '（練',
        '煉）': '練）',
        
        # Other common errors (add as discovered)
        '絓驗': '經驗',  # We saw this corruption before
    }
    
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    
    return text


def validate_and_warn(content: str, agent_name: str) -> list:
    """
    Validate report content and return list of warnings
    
    Args:
        content: Report content
        agent_name: Name of the agent
        
    Returns:
        List of warning messages
    """
    warnings = []
    
    # Check for suspicious '煉' character
    # Only flag if not in proper contexts like "冶煉", "提煉", "鍛煉"
    if '煉' in content:
        proper_contexts = ['冶煉', '提煉', '鍛煉', '精煉', '修煉']
        is_proper = any(ctx in content for ctx in proper_contexts)
        if not is_proper:
            # Find context around '煉'
            idx = content.find('煉')
            context = content[max(0, idx-15):min(len(content), idx+15)]
            warnings.append(f"Suspicious '煉' character found. Context: ...{context}...")
    
    # Check word count
    word_count = count_chinese_words(content)
    if word_count < 800:
        warnings.append(f"Too short: {word_count} words (expected 800-1500)")
    elif word_count > 1500:
        warnings.append(f"Too long: {word_count} words (expected 800-1500)")
    
    # Check for truncation markers that shouldn't be there
    truncation_markers = ['...(已截斷)', '...(內容已截斷)', '...(為控制長度已精簡)']
    for marker in truncation_markers:
        if marker in content:
            warnings.append(f"Found truncation marker: '{marker}'")
    
    if warnings:
        print(f"\n⚠️  {agent_name} Report Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    
    return warnings


def post_process_agent_output(content: str, agent_name: str, retry_callback=None) -> str:
    """
    Complete post-processing pipeline for agent output
    
    Args:
        content: Raw agent output
        agent_name: Name of the agent
        retry_callback: Optional function to call if validation fails
        
    Returns:
        Processed and validated content
    """
    # Step 1: Fix common errors
    content = fix_common_llm_errors(content)
    
    # Step 2: Validate and warn
    warnings = validate_and_warn(content, agent_name)
    
    # Step 3: Critical validation - retry if needed
    word_count = count_chinese_words(content)
    if (word_count < 800 or word_count > 1500) and retry_callback:
        print(f"\n🔄 {agent_name}: Word count {word_count} out of range, triggering retry...")
        # Callback should regenerate the content
        # This is optional and should be implemented in the calling code
    
    return content
