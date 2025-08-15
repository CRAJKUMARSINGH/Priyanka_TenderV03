#!/usr/bin/env python3
"""
End-to-end test for the bill transformation batch processing pipeline.

This script tests the complete workflow from input Excel files to final output verification.
"""

import os
import sys
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('e2e_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Import local modules
sys.path.append(str(Path(__file__).parent))
from batch_processor import process_batch_files
from verify_output import OutputVerifier

class EndToEndTester:
    """Tests the complete bill transformation pipeline."""
    
    def __init__(self, test_files_dir: str = 'test_files'):
        """Initialize the tester with the directory containing test files."""
        self.test_files_dir = Path(test_files_dir)
        self.output_dir = Path('test_output')
        self.temp_dir = Path(tempfile.mkdtemp(prefix='bill_test_'))
        self.test_files: list[Path] = []
        self.results: dict = {}
    
    def setup(self) -> bool:
        """Set up the test environment."""
        logger.info("Setting up test environment...")
        
        # Clean up previous test output
        self.cleanup()
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Find test files
        self.test_files = list(self.test_files_dir.glob('*.xlsx'))
        if not self.test_files:
            logger.error("No test files found in %s", self.test_files_dir)
            return False
        
        logger.info("Found %d test files", len(self.test_files))
        return True
    
    def run_batch_processing(self) -> bool:
        """Run the batch processing on test files."""
        logger.info("Starting batch processing...")
        
        try:
            self.results = process_batch_files(
                input_files=[str(f) for f in self.test_files],
                output_dir=str(self.output_dir),
                reverse_font=False,
                generate_html=True,
                generate_pdf=True,
                generate_docx=True
            )
            
            if not self.results.get('status') == 'completed':
                logger.error("Batch processing failed")
                return False
                
            logger.info("Batch processing completed successfully")
            return True
            
        except Exception as e:
            logger.exception("Error during batch processing")
            return False
    
    def verify_output(self) -> bool:
        """Verify the output files."""
        logger.info("Verifying output files...")
        
        verifier = OutputVerifier(str(self.output_dir))
        return verifier.run_verification()
    
    def run_tests(self) -> bool:
        """Run all tests and return overall success status."""
        logger.info("=" * 50)
        logger.info("STARTING END-TO-END TEST")
        logger.info("=" * 50)
        
        # Set up test environment
        if not self.setup():
            return False
        
        # Run batch processing
        if not self.run_batch_processing():
            logger.error("❌ End-to-end test failed during batch processing")
            return False
        
        # Verify output
        if not self.verify_output():
            logger.error("❌ End-to-end test failed during output verification")
            return False
        
        logger.info("✅ End-to-end test completed successfully")
        return True
    
    def cleanup(self) -> None:
        """Clean up test artifacts."""
        # Remove output directory if it exists
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir, ignore_errors=True)
        
        # Remove temp directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Clean up log files
        for log_file in ['e2e_test.log', 'verification.log', 'batch_processing.log']:
            if os.path.exists(log_file):
                try:
                    os.remove(log_file)
                except:
                    pass

def main() -> int:
    """Main entry point for the end-to-end test."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run end-to-end tests for bill transformation.')
    parser.add_argument(
        '--test-files-dir',
        default='test_files',
        help='Directory containing test Excel files (default: test_files)'
    )
    parser.add_argument(
        '--output-dir',
        default='test_output',
        help='Directory to store test output (default: test_output)'
    )
    
    args = parser.parse_args()
    
    tester = EndToEndTester(test_files_dir=args.test_files_dir)
    tester.output_dir = Path(args.output_dir)
    
    success = tester.run_tests()
    
    # Print final status
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Status: {'PASSED' if success else 'FAILED'}")
    print(f"Log file: {os.path.abspath('e2e_test.log')}")
    print("=" * 50 + "\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error in end-to-end test")
        print(f"\nError: {str(e)}")
        print("Check e2e_test.log for details")
        sys.exit(1)
