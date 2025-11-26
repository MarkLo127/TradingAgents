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
        
        # Try to register custom Cactus Classical Serif font first
        self.custom_font = None
        
        # Ensure we have the absolute path to the current file
        current_file = os.path.abspath(__file__)
        # backend/app/services/pdf_generator.py -> backend/app/services -> backend/app -> backend -> root
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        
        custom_font_path = os.path.join(
            root_dir,
            'Cactus_Classical_Serif',
            'CactusClassicalSerif-Regular.ttf'
        )
        
        print(f"Attempting to load font from: {custom_font_path}")
        
        if os.path.exists(custom_font_path):
            try:
                pdfmetrics.registerFont(TTFont('CactusClassicalSerif', custom_font_path))
                self.custom_font = 'CactusClassicalSerif'
                print(f"Successfully registered Cactus Classical Serif font")
            except Exception as e:
                print(f"Error registering custom font: {e}")
        else:
            print(f"Custom font file not found at {custom_font_path}")
            # Try looking in current working directory as fallback
            cwd_path = os.path.join(os.getcwd(), 'Cactus_Classical_Serif', 'CactusClassicalSerif-Regular.ttf')
            if os.path.exists(cwd_path):
                 try:
                    pdfmetrics.registerFont(TTFont('CactusClassicalSerif', cwd_path))
                    self.custom_font = 'CactusClassicalSerif'
                    print(f"Successfully registered Cactus Classical Serif font from CWD")
                 except Exception as e:
                    print(f"Error registering custom font from CWD: {e}")

        # Register Chinese font as fallback for CJK characters
        if not self.custom_font:
            try:
                # Register Chinese font (Traditional Chinese support)
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                self.chinese_font = 'STSong-Light'
                print("Registered STSong-Light as fallback (Warning: May not be visible in all viewers)")
            except Exception as e:
                # If CID font registration fails, try alternative method
                try:
                    pdfmetrics.registerFont(UnicodeCIDFont('STHeiti-Light'))
                    self.chinese_font = 'STHeiti-Light'
                except Exception:
                    # Last resort: use MSung for Traditional Chinese
                    try:
                        pdfmetrics.registerFont(UnicodeCIDFont('MSung-Light'))
                        self.chinese_font = 'MSung-Light'
                    except Exception:
                        # Fallback to basic font
                        self.chinese_font = 'Helvetica'
                        print("Warning: Could not register Chinese font")
        else:
            self.chinese_font = self.custom_font
        
        # Set primary font: use custom font if available, otherwise Chinese font
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
        content = self._clean_markdown(report_content)
        
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
        Fixes spurious character issues and improves cleaning logic
        
        Args:
            text: Markdown text
            
        Returns:
            Cleaned text
        """
        # 1. Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # 2. Remove bold markers (improved version)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        
        # 3. Remove italic markers (more precise to avoid side effects)
        text = re.sub(r'(?<![\*_])\*([^\*\n]+?)\*(?![\*_])', r'\1', text)
        text = re.sub(r'(?<![\*_])_([^_\n]+?)_(?![\*_])', r'\1', text)
        
        # 4. Remove underscore bold
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # 5. Remove code blocks
        text = re.sub(r'```[^`]*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+?)`', r'\1', text)
        
        # 6. Clean up bullet points
        text = re.sub(r'^\s*[\*\-\+]\s+', '• ', text, flags=re.MULTILINE)
        
        # 7. Remove horizontal rules
        text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
        
        # 8. Clean table separators
        text = re.sub(r'^\s*\|?\s*:?-+:?\s*\|?\s*$', '', text, flags=re.MULTILINE)
        
        # 9. Remove table | symbols (keep content)
        text = re.sub(r'^\s*\|', '', text, flags=re.MULTILINE)
        text = re.sub(r'\|\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\|', ' | ', text)
        
        # 10. Clean excess spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # 11. Clean excess blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 12. Remove isolated markdown symbols (more cautious to avoid spurious chars)
        text = re.sub(r'(?<=\s)[\*_`~#]+(?=\s)', '', text)
        text = re.sub(r'^[\*_`~#]+(?=\s)', '', text, flags=re.MULTILINE)
        text = re.sub(r'(?<=\s)[\*_`~#]+$', '', text, flags=re.MULTILINE)
        
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
