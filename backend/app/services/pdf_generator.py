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
        # Register Chinese fonts using reportlab's built-in CID fonts
        # These fonts support Chinese characters without requiring external font files
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        
        try:
            # Register Chinese font (Traditional Chinese support)
            # 'STSong-Light' is a built-in CID font that supports Chinese characters
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            self.chinese_font = 'STSong-Light'
        except Exception as e:
            # If CID font registration fails, try alternative method
            try:
                # Try STHeiti for better Traditional Chinese support
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
                    print("Warning: Could not register Chinese font, Chinese characters may not display correctly")
    
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
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles with Chinese font support
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=self.chinese_font,
            fontSize=24,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=12,
            textColor=HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER,
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=16,
            textColor=HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            leading=14,
            textColor=HexColor('#333333'),
            spaceAfter=8,
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
                try:
                    elements.append(Paragraph(text, body_style))
                except Exception as e:
                    # If paragraph fails, add as plain text
                    elements.append(Paragraph(text.encode('ascii', 'xmlcharrefreplace').decode(), body_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get the PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def _clean_markdown(self, text: str) -> str:
        """
        Clean markdown formatting for PDF
        
        Args:
            text: Markdown text
            
        Returns:
            Cleaned text
        """
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove bold/italic markers
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
        # Remove code blocks
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Clean up bullet points
        text = re.sub(r'^\s*[\*\-\+]\s+', '• ', text, flags=re.MULTILINE)
        
        # Remove horizontal rules
        text = re.sub(r'^[\-\*\_]{3,}\s*$', '', text, flags=re.MULTILINE)
        
        return text
    
    def _escape_html(self, text: str) -> str:
        """
        Escape HTML special characters for PDF
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
