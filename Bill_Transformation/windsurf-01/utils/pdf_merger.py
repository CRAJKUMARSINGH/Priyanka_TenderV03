"""
PDF merging utilities for the Windsurf Billing System.

This module provides functionality to merge multiple PDF files into a single PDF.
"""

from PyPDF2 import PdfMerger, PdfReader
from typing import List, Union, BinaryIO
import io
import logging

logger = logging.getLogger(__name__)

class PDFMerger:
    """Handles merging of multiple PDF files into a single PDF."""
    
    def __init__(self):
        """Initialize the PDF merger."""
        self.merger = PdfMerger()
    
    def add_pdf(self, pdf_file: Union[str, BinaryIO, bytes]) -> bool:
        """Add a PDF file to the merger.
        
        Args:
            pdf_file: Path to PDF file, file-like object, or bytes content
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            if isinstance(pdf_file, bytes):
                # Handle bytes input
                self.merger.append(io.BytesIO(pdf_file))
            else:
                # Handle file path or file-like object
                self.merger.append(pdf_file)
            return True
        except Exception as e:
            logger.error(f"Error adding PDF to merger: {e}")
            return False
    
    def merge(self, output_path: str = None) -> Union[bytes, bool]:
        """Merge all added PDFs and save or return the result.
        
        Args:
            output_path: If provided, save merged PDF to this path.
                        If None, return merged PDF as bytes.
                        
        Returns:
            Union[bytes, bool]: Merged PDF as bytes if output_path is None,
                              otherwise True if saved successfully, False otherwise.
        """
        try:
            if output_path:
                # Save to file
                with open(output_path, 'wb') as f:
                    self.merger.write(f)
                return True
            else:
                # Return as bytes
                output = io.BytesIO()
                self.merger.write(output)
                return output.getvalue()
        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            return False if output_path else b''
        finally:
            self.merger.close()
    
    def get_page_count(self, pdf_file: Union[str, BinaryIO, bytes]) -> int:
        """Get the number of pages in a PDF file.
        
        Args:
            pdf_file: Path to PDF file, file-like object, or bytes content
            
        Returns:
            int: Number of pages, or 0 if error
        """
        try:
            if isinstance(pdf_file, bytes):
                reader = PdfReader(io.BytesIO(pdf_file))
            else:
                reader = PdfReader(pdf_file)
            return len(reader.pages)
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            return 0
