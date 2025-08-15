#!/usr/bin/env python3
"""
Output Verification for Bill Transformation

This script verifies that all required output files are generated correctly
and meet the specified requirements.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional
import zipfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('verification.log')
    ]
)
logger = logging.getLogger(__name__)

# Required templates and extensions
REQUIRED_TEMPLATES = [
    'first_page',
    'deviation_statement',
    'extra_items',
    'note_sheet',
    'certificate_ii',
    'certificate_iii'
]

REQUIRED_EXTENSIONS = ['.html', '.pdf', '.docx']

class OutputVerifier:
    """Verifies the output of the batch processing."""
    
    def __init__(self, output_dir: str = 'batch_processing_output'):
        self.output_dir = Path(output_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.file_count = 0
        self.bill_count = 0
    
    def run_verification(self) -> bool:
        """Run all verification checks."""
        logger.info("Starting output verification...")
        
        # Check if output directory exists
        if not self.output_dir.exists():
            self._add_error(f"Output directory not found: {self.output_dir}")
            return False
        
        # Find all bill directories
        bill_dirs = [d for d in self.output_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        self.bill_count = len(bill_dirs)
        
        if self.bill_count == 0:
            self._add_error("No bill directories found in the output directory")
            return False
        
        logger.info(f"Found {self.bill_count} bill directories to verify")
        
        # Verify each bill directory
        for bill_dir in bill_dirs:
            self._verify_bill_directory(bill_dir)
        
        # Check ZIP file
        zip_files = list(self.output_dir.glob('*.zip'))
        if not zip_files:
            self._add_warning("No ZIP archive found in the output directory")
        else:
            self._verify_zip_file(zip_files[0])
        
        # Print summary
        self._print_summary()
        
        return len(self.errors) == 0
    
    def _verify_bill_directory(self, bill_dir: Path) -> None:
        """Verify the contents of a single bill directory."""
        logger.info(f"Verifying bill directory: {bill_dir.name}")
        
        # Check for required files
        found_files = set(f.name for f in bill_dir.iterdir() if f.is_file())
        missing_files = []
        
        for template in REQUIRED_TEMPLATES:
            for ext in REQUIRED_EXTENSIONS:
                filename = f"{template}{ext}"
                if filename not in found_files:
                    missing_files.append(filename)
                else:
                    self.file_count += 1
        
        if missing_files:
            self._add_error(
                f"Missing files in {bill_dir.name}: {', '.join(missing_files)}"
            )
        
        # Check file sizes (non-zero)
        for file in bill_dir.iterdir():
            if file.is_file() and file.stat().st_size == 0:
                self._add_error(f"Empty file: {file}")
    
    def _verify_zip_file(self, zip_path: Path) -> None:
        """Verify the contents of the ZIP archive."""
        logger.info(f"Verifying ZIP file: {zip_path.name}")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check if ZIP is not empty
                file_list = zip_ref.namelist()
                if not file_list:
                    self._add_error("ZIP file is empty")
                    return
                
                # Check for expected number of files
                expected_file_count = self.bill_count * len(REQUIRED_TEMPLATES) * len(REQUIRED_EXTENSIONS)
                if len(file_list) < expected_file_count:
                    self._add_warning(
                        f"ZIP file may be incomplete. Expected at least {expected_file_count} files, "
                        f"found {len(file_list)}"
                    )
                
                # Check for zero-sized files in the ZIP
                for file in file_list:
                    info = zip_ref.getinfo(file)
                    if info.file_size == 0:
                        self._add_error(f"Empty file in ZIP: {file}")
                        
        except zipfile.BadZipFile:
            self._add_error(f"Invalid ZIP file: {zip_path}")
        except Exception as e:
            self._add_error(f"Error reading ZIP file {zip_path}: {str(e)}")
    
    def _add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        logger.error(message)
    
    def _add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
        logger.warning(message)
    
    def _print_summary(self) -> None:
        """Print a summary of the verification results."""
        print("\n" + "=" * 50)
        print("VERIFICATION SUMMARY")
        print("=" * 50)
        
        print(f"\n• Verified {self.bill_count} bill directories")
        print(f"• Verified {self.file_count} output files")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            print("\n❌ Verification failed")
        else:
            print("\n✅ Verification passed successfully")
        
        print("\nDetailed logs available in: verification.log")
        print("=" * 50 + "\n")

def main() -> int:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify batch processing output.')
    parser.add_argument(
        '--output-dir',
        default='batch_processing_output',
        help='Directory containing the output files to verify (default: batch_processing_output)'
    )
    
    args = parser.parse_args()
    
    verifier = OutputVerifier(args.output_dir)
    success = verifier.run_verification()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
