# -*- coding: utf-8 -*-
"""
PDF Generation Service for Analyst Reports
Converts markdown reports to PDF format with Chinese character support
"""
import io
import re
from typing import Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import markdown


class PDFGenerator:
    """Generate PDF reports from markdown content"""
    
    def __init__(self):
        """Initialize PDF generator with Chinese font support"""
        import os
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        
        # Initialize font variables
        self.custom_font = None
        self.chinese_font = None
        
        # Ensure we have the absolute path to the current file
        current_file = os.path.abspath(__file__)
        # backend/app/services/pdf_generator.py -> backend/app/services -> backend/app -> backend -> root
        # CRITICAL FIX: Use system fonts for maximum compatibility
        # Arial Unicode MS supports: Chinese, English, Math symbols, Emoji
        # This avoids font file loading issues with ReportLab
        try:
            # Try to use Arial Unicode MS (best for all characters)
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # macOS system font path
            arial_unicode_path = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
            if os.path.exists(arial_unicode_path):
                pdfmetrics.registerFont(TTFont('ArialUnicode', arial_unicode_path))
                self.custom_font = 'ArialUnicode'
                self.chinese_font = 'ArialUnicode'
                print(f"✅ Successfully registered Arial Unicode MS (supports Chinese, English, Math, Emoji)")
            else:
                # Fallback: Use built-in Helvetica (limited Chinese support)
                self.custom_font = 'Helvetica'
                self.chinese_font = 'Helvetica'
                print(f"⚠️  Using Helvetica (limited Chinese character support)")
        except Exception as e:
            print(f"❌ Font registration error: {e}")
            self.custom_font = 'Helvetica'
            self.chinese_font = 'Helvetica'
        
        # Set primary font
        self.primary_font = self.custom_font if self.custom_font else self.chinese_font
    
    def generate_analyst_report_pdf(
        self,
        analyst_name: str,
        ticker: str,
        analysis_date: str,
        report_content: str,
    ) -> bytes:
        """
        Generate a PDF from analyst report content
        
        Args:
            analyst_name: Name of the analyst
            ticker: Stock ticker symbol
            analysis_date: Date of analysis
            report_content: Markdown formatted report content
            
        Returns:
            PDF file content as bytes
        """
        buffer = io.BytesIO()
        
        # Create PDF document with reduced margins for more content space
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm,
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles with proper spacing and wrapping
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=self.primary_font,
            fontSize=24,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            wordWrap='CJK',
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontName=self.primary_font,
            fontSize=12,
            textColor=HexColor('#666666'),
            spaceAfter=12,
            alignment=TA_CENTER,
            wordWrap='CJK',
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=self.primary_font,
            fontSize=16,
            textColor=HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=16,
            wordWrap='CJK',
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName=self.primary_font,
            fontSize=9,
            leading=14,
            textColor=HexColor('#333333'),
            spaceAfter=8,
            wordWrap='CJK',
            splitLongWords=True,
            allowOrphans=0,
            allowWidows=0,
        )
        
        # Add title
        title = f"{analyst_name}"
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.3*cm))
        
        # Add metadata
        metadata = f"{ticker} | {analysis_date}"
        elements.append(Paragraph(metadata, subtitle_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Convert markdown to simple text (basic conversion)
        # Clean markdown formatting
        # DEBUG: Log content before PDF conversion
        print(f"\n[PDF DEBUG] Content BEFORE _clean_markdown:")
        if '煉' in report_content:
            print(f"  ⚠️  Found '煉' in original content")
        if '練' in report_content:
            print(f"  ✅ Found '練' in original content")
        
        content = self._clean_markdown(report_content)
        
        # DEBUG: Log content after cleaning
        print(f"[PDF DEBUG] Content AFTER _clean_markdown:")
        if '煉' in content:
            print(f"  ⚠️  Found '煉' AFTER cleaning")
        if '練' in content:
            print(f"  ✅ Found '練' AFTER cleaning")
        
        # Split content into paragraphs
        paragraphs = content.split('\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                elements.append(Spacer(1, 0.2*cm))
                continue
            
            # Check if it's a heading
            if para.startswith('# '):
                text = para[2:]
                elements.append(Paragraph(text, heading_style))
            elif para.startswith('## '):
                text = para[3:]
                elements.append(Paragraph(text, heading_style))
            elif para.startswith('### '):
                text = para[4:]
                elements.append(Paragraph(text, heading_style))
            else:
                # Regular paragraph - escape HTML chars and handle special characters
                text = self._escape_html(para)
                # Ensure proper UTF-8 handling
                elements.append(Paragraph(text, body_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get the PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def _clean_markdown(self, text: str) -> str:
        """
        Clean markdown formatting for PDF - IMPROVED VERSION
        Simplified regex patterns to prevent encoding artifacts
        
        Args:
            text: Markdown text
            
        Returns:
            Cleaned text
        """
        import unicodedata
        
        # 0. Normalize Unicode to prevent encoding issues
        text = unicodedata.normalize('NFKC', text)
        
        # 1. Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # 2. Remove bold markers (simplified version)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # 3. Remove italic markers (SIMPLIFIED - avoid complex lookahead/lookbehind)
        # Only match single * or _ that are NOT part of ** or __
        text = re.sub(r'(?<![\*])\*([^\*]+?)\*(?![\*])', r'\1', text)
        text = re.sub(r'(?<![_])_([^_]+?)_(?![_])', r'\1', text)
        
        # 4. Remove code blocks
        text = re.sub(r'```[^`]*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+?)`', r'\1', text)
        
        # 5. Clean up bullet points
        text = re.sub(r'^\s*[\*\-\+]\s+', '• ', text, flags=re.MULTILINE)
        
        # 6. Remove horizontal rules
        text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
        
        # 7. Clean table separators (simplified)
        text = re.sub(r'^\s*\|?\s*:?-+:?\s*\|?\s*$', '', text, flags=re.MULTILINE)
        
        # 8. Remove table | symbols (keep content)
        text = re.sub(r'^\s*\|', '', text, flags=re.MULTILINE)
        text = re.sub(r'\|\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\|', ' | ', text)
        
        # 9. Clean excess spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # 10. Clean excess blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 11. Remove isolated markdown symbols (SIMPLIFIED - no complex patterns)
        # Remove lines that only contain markdown symbols
        text = re.sub(r'^[\*_`~#\-\+]+\s*$', '', text, flags=re.MULTILINE)
        
        # 12. REMOVED problematic Unicode filter that was corrupting Chinese characters
        # The string comparison '\u4e00' <= char <= '\u9fff' was comparing UTF-8 bytes,
        # not Unicode code points, causing characters like '經' to be corrupted.
        # Unicode normalization at the start (line 237) is sufficient.
        
        return text.strip()
    
    def _escape_html(self, text: str) -> str:
        """
        Escape HTML special characters for PDF - IMPROVED VERSION
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # Escape in order to avoid double-escaping
        replacements = [
            ('&', '&amp;'),
            ('<', '&lt;'),
            ('>', '&gt;'),
            ('"', '&quot;'),
            ("'", '&apos;'),
        ]
        
        for old, new in replacements:
            text = text.replace(old, new)
        
        return text
