"""
Batch Processor for Windsurf Billing System

This module provides batch processing functionality for handling multiple bills
in a single operation, with support for various output formats.
"""

import os
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional, BinaryIO, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Handles batch processing of multiple bill files."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the batch processor.
        
        Args:
            output_dir: Directory to save processed files. If None, a temporary
                      directory will be created.
        """
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.mkdtemp())
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def process_batch(
        self,
        input_files: List[Union[str, Path, BinaryIO]],
        premium_percentage: float = 10.0,
        reverse_font: bool = False,
        output_formats: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """Process multiple bill files in a batch."""
        if output_formats is None:
            output_formats = {'html': True, 'pdf': True, 'docx': True}
            
        results = {
            'successful': [],
            'failed': [],
            'output_files': [],
            'output_dir': str(self.output_dir)
        }
        
        for file_idx, input_file in enumerate(input_files, 1):
            try:
                file_result = self._process_single_file(
                    input_file, file_idx, premium_percentage, 
                    reverse_font, output_formats
                )
                results['successful'].append(file_result)
                results['output_files'].extend(file_result.get('output_files', []))
                
            except Exception as e:
                file_path = str(input_file) if not hasattr(input_file, 'name') else input_file.name
                error_msg = f"Error processing file {file_path}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                results['failed'].append({
                    'file': file_path,
                    'error': str(e)
                })
        
        # Create a zip archive of all output files
        if results['output_files']:
            zip_path = self._create_zip_archive(results['output_files'])
            results['zip_archive'] = str(zip_path)
            
        return results
    
    def _process_single_file(
        self,
        input_file: Union[str, Path, BinaryIO],
        file_idx: int,
        premium_percentage: float,
        reverse_font: bool,
        output_formats: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Process a single bill file."""
        result = {
            'file_name': str(input_file) if not hasattr(input_file, 'name') else input_file.name,
            'output_files': [],
            'processing_time': datetime.now().isoformat()
        }
        
        # Generate a base name for output files
        base_name = f"bill_{file_idx:03d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate outputs based on requested formats
        if output_formats.get('html', False):
            html_path = self._generate_html({}, base_name)  # Pass actual data
            result['output_files'].append(('html', str(html_path)))
            
        if output_formats.get('pdf', False):
            pdf_path = self._generate_pdf({}, base_name)  # Pass actual data
            result['output_files'].append(('pdf', str(pdf_path)))
            
        if output_formats.get('docx', False):
            docx_path = self._generate_docx({}, base_name)  # Pass actual data
            result['output_files'].append(('docx', str(docx_path)))
            
        result['status'] = 'success'
        return result
    
    def _generate_html(self, data: Dict[str, Any], base_name: str) -> Path:
        """Generate HTML output for a bill."""
        output_path = self.output_dir / f"{base_name}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("<html><body><h1>Bill Output</h1></body></html>")
        return output_path
    
    def _generate_pdf(self, data: Dict[str, Any], base_name: str) -> Path:
        """Generate PDF output for a bill."""
        output_path = self.output_dir / f"{base_name}.pdf"
        # Placeholder - implement actual PDF generation
        with open(output_path, 'wb') as f:
            f.write(b"%PDF-1.4\n%PDF placeholder")
        return output_path
    
    def _generate_docx(self, data: Dict[str, Any], base_name: str) -> Path:
        """Generate DOCX output for a bill."""
        output_path = self.output_dir / f"{base_name}.docx"
        # Placeholder - implement actual DOCX generation
        with open(output_path, 'wb') as f:
            f.write(b"DOCX placeholder")
        return output_path
    
    def _create_zip_archive(self, files: List[tuple]) -> Path:
        """Create a ZIP archive of all output files."""
        zip_path = self.output_dir / "bills_bundle.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for _, file_path in files:
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.basename(file_path))
        return zip_path
