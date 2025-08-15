"""
Test Script for Batch Processing

This script tests the batch processing functionality of the Windsurf Billing System.
It processes sample Excel files and validates the output documents.
"""

import os
import sys
import logging
from pathlib import Path
import shutil
from datetime import datetime

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

# Import BatchProcessor
from windsurf.batch_processor import BatchProcessor

def main():
    # Set up test directory
    test_dir = Path(r"C:\Users\Rajkumar\Bill_Transformation\test_files")
    if not test_dir.exists():
        print(f"Error: Test directory not found at {test_dir}")
        return 1
    
    # Get all Excel files from test directory
    input_files = list(test_dir.glob("*.xlsx"))
    if not input_files:
        print("No Excel files found in test directory")
        return 1
    
    print(f"Found {len(input_files)} Excel files for processing")
    
    # Create output directory
    output_dir = Path("batch_processing_output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize batch processor
    processor = BatchProcessor(output_dir=output_dir)
    
    # Process files
    print("Starting batch processing...")
    results = processor.process_batch(
        input_files=input_files,
        premium_percentage=10.0,
        reverse_font=False,
        output_formats={
            'html': True,
            'pdf': True,
            'docx': True
        }
    )
    
    # Print results
    print("\nBatch processing completed!")
    print(f"Successfully processed: {len(results['successful'])} files")
    print(f"Failed to process: {len(results['failed'])} files")
    
    if results['failed']:
        print("\nFailed files:")
        for fail in results['failed']:
            print(f"- {fail['file']}: {fail['error']}")
    
    if 'zip_archive' in results:
        print(f"\nOutput files bundled in: {results['zip_archive']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
