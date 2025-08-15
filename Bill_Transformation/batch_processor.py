#!/usr/bin/env python3
"""
Batch Processor for Bill Transformation

This module handles batch processing of multiple bill files, generating
output documents in various formats (HTML, PDF, DOCX) using the specified
templates and configurations.
"""

import os
import sys
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('batch_processing.log')
    ]
)
logger = logging.getLogger(__name__)

# Import document generator and excel processor
from excel_processor_v01 import ExcelProcessorV01
from document_generator_v04 import DocumentGeneratorV04

def process_single_file(
    input_file: str,
    output_dir: str,
    reverse_font: bool,
    generate_html: bool = True,
    generate_pdf: bool = True,
    generate_docx: bool = True
) -> Dict[str, Any]:
    """
    Process a single bill file and generate output documents.
    
    Args:
        input_file: Path to the input Excel file
        output_dir: Base directory for output files
        reverse_font: Whether to use reverse font in output
        generate_html: Whether to generate HTML output
        generate_pdf: Whether to generate PDF output
        generate_docx: Whether to generate DOCX output
        
    Returns:
        Dictionary with processing results and metadata
    """
    start_time = datetime.now()
    file_name = Path(input_file).stem
    file_output_dir = Path(output_dir) / f"bill_{file_name}_{start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create output directory
        file_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process Excel file
        logger.info(f"Processing file: {input_file}")
        processor = ExcelProcessorV01()
        data = processor.process_excel(input_file)
        
        # Generate documents
        generator = DocumentGeneratorV04()
        generator.generate_html = generate_html
        generator.generate_pdf = generate_pdf
        generator.generate_docx = generate_docx
        
        # Set output directory
        generator.output_dir = str(file_output_dir)
        
        # Generate all documents
        generated_files = generator.generate_all_documents(
            data,
            reverse_font=reverse_font
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'status': 'success',
            'input_file': input_file,
            'output_dir': str(file_output_dir),
            'generated_files': generated_files,
            'processing_time_seconds': processing_time,
            'error': None
        }
        
    except Exception as e:
        error_msg = f"Error processing {input_file}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            'status': 'error',
            'input_file': input_file,
            'output_dir': str(file_output_dir) if 'file_output_dir' in locals() else None,
            'generated_files': [],
            'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
            'error': str(e)
        }

def process_batch_files(
    input_files: List[str],
    output_dir: str = 'batch_processing_output',
    reverse_font: bool = False,
    generate_html: bool = True,
    generate_pdf: bool = True,
    generate_docx: bool = True,
    max_workers: int = 4
) -> Dict[str, Any]:
    """
    Process multiple bill files in batch.
    
    Args:
        input_files: List of input Excel files
        output_dir: Base directory for output files
        reverse_font: Whether to use reverse font in output
        generate_html: Whether to generate HTML output
        generate_pdf: Whether to generate PDF output
        generate_docx: Whether to generate DOCX output
        max_workers: Maximum number of parallel workers
        
    Returns:
        Dictionary with batch processing results and statistics
    """
    start_time = datetime.now()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting batch processing of {len(input_files)} files")
    logger.info(f"Output directory: {output_dir.absolute()}")
    
    # Process files in parallel
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(
                process_single_file,
                input_file,
                output_dir,
                reverse_font=reverse_font,
                generate_html=generate_html,
                generate_pdf=generate_pdf,
                generate_docx=generate_docx
            ): input_file for input_file in input_files
        }
        
        # Process completed tasks
        for future in as_completed(future_to_file):
            input_file = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                
                if result['status'] == 'success':
                    logger.info(f"Completed: {input_file} in {result['processing_time_seconds']:.2f}s")
                else:
                    logger.error(f"Failed: {input_file} - {result['error']}")
                    
            except Exception as e:
                error_msg = f"Unexpected error processing {input_file}: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                
                results.append({
                    'status': 'error',
                    'input_file': input_file,
                    'output_dir': None,
                    'generated_files': [],
                    'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
                    'error': error_msg
                })
    
    # Calculate statistics
    total_time = (datetime.now() - start_time).total_seconds()
    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = len(results) - success_count
    
    # Create summary
    summary = {
        'total_files': len(input_files),
        'success_count': success_count,
        'error_count': error_count,
        'total_processing_time_seconds': total_time,
        'avg_processing_time_seconds': total_time / len(input_files) if input_files else 0,
        'results': results,
        'success': error_count == 0,
        'start_time': start_time.isoformat(),
        'end_time': datetime.now().isoformat()
    }
    
    logger.info(f"Batch processing completed in {total_time:.2f} seconds")
    logger.info(f"Success: {success_count}, Failed: {error_count}")
    
    return summary

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process bill files in batch')
    parser.add_argument('input_files', nargs='+', help='Input Excel files')
    parser.add_argument('--output-dir', default='batch_processing_output', help='Output directory')
    parser.add_argument('--reverse-font', action='store_true', help='Use reverse font')
    parser.add_argument('--no-html', action='store_false', dest='html', help='Skip HTML generation')
    parser.add_argument('--no-pdf', action='store_false', dest='pdf', help='Skip PDF generation')
    parser.add_argument('--no-docx', action='store_false', dest='docx', help='Skip DOCX generation')
    parser.add_argument('--workers', type=int, default=4, help='Maximum number of parallel workers')
    
    args = parser.parse_args()
    
    result = process_batch_files(
        input_files=args.input_files,
        output_dir=args.output_dir,
        reverse_font=args.reverse_font,
        generate_html=args.html,
        generate_pdf=args.pdf,
        generate_docx=args.docx,
        max_workers=args.workers
    )
    
    sys.exit(0 if result['success'] else 1)
