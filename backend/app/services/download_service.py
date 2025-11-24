"""
Download Service for Analyst Reports
Handles single PDF and multiple PDF ZIP downloads
"""
import io
import zipfile
from typing import List, Dict, Optional
from datetime import datetime

from backend.app.services.pdf_generator import PDFGenerator


class DownloadService:
    """Service for handling analyst report downloads"""
    
    def __init__(self):
        """Initialize download service"""
        self.pdf_generator = PDFGenerator()
    
    def create_single_pdf(
        self,
        analyst_name: str,
        ticker: str,
        analysis_date: str,
        report_content: str,
    ) -> tuple[bytes, str]:
        """
        Create a PDF for a single analyst report
        
        Args:
            analyst_name: Name of the analyst
            ticker: Stock ticker symbol
            analysis_date: Date of analysis (YYYY-MM-DD)
            report_content: Markdown formatted report content
            
        Returns:
            Tuple of (PDF bytes, filename)
        """
        # Generate PDF
        pdf_bytes = self.pdf_generator.generate_analyst_report_pdf(
            analyst_name=analyst_name,
            ticker=ticker,
            analysis_date=analysis_date,
            report_content=report_content,
        )
        
        # Generate filename: 股票代號_分析師_日期.pdf
        filename = f"{ticker}_{analyst_name}_{analysis_date}.pdf"
        
        return pdf_bytes, filename
    
    def create_multiple_pdfs_zip(
        self,
        ticker: str,
        analysis_date: str,
        reports: List[Dict[str, str]],
    ) -> tuple[bytes, str]:
        """
        Create a ZIP file containing multiple analyst report PDFs
        
        Args:
            ticker: Stock ticker symbol
            analysis_date: Date of analysis (YYYY-MM-DD)
            reports: List of dicts with keys 'analyst_name' and 'report_content'
            
        Returns:
            Tuple of (ZIP bytes, filename)
        """
        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for report in reports:
                analyst_name = report.get('analyst_name', 'Unknown')
                report_content = report.get('report_content', '')
                
                # Skip if no content
                if not report_content:
                    continue
                
                # Generate PDF for this analyst
                pdf_bytes = self.pdf_generator.generate_analyst_report_pdf(
                    analyst_name=analyst_name,
                    ticker=ticker,
                    analysis_date=analysis_date,
                    report_content=report_content,
                )
                
                # Add to ZIP with proper filename
                pdf_filename = f"{ticker}_{analyst_name}_{analysis_date}.pdf"
                zip_file.writestr(pdf_filename, pdf_bytes)
        
        # Get ZIP content
        zip_bytes = zip_buffer.getvalue()
        zip_buffer.close()
        
        # Generate ZIP filename: 股票代號_日期.zip
        zip_filename = f"{ticker}_{analysis_date}.zip"
        
        return zip_bytes, zip_filename


# Singleton instance
download_service = DownloadService()
