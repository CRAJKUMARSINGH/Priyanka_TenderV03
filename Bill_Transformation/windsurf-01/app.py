"""
Windsurf Billing System - Main Application

This module provides the core functionality for the Windsurf billing system,
including document generation and template processing.
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('windsurf.log')
    ]
)
logger = logging.getLogger(__name__)

class WindsurfApp:
    """Main application class for the Windsurf Billing System."""
    
    def __init__(self, template_dir: Optional[str] = None):
        """Initialize the Windsurf application.
        
        Args:
            template_dir: Directory containing the template files.
                        Defaults to 'templates' in the package directory.
        """
        self.base_dir = Path(__file__).parent.parent
        self.template_dir = Path(template_dir) if template_dir else self.base_dir / 'templates'
        self.template_tex_dir = self.base_dir / 'templates_latex'
        
        # Ensure template directories exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.template_tex_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate templates
        self._validate_templates()
        
        logger.info("Windsurf application initialized")
    
    def _validate_templates(self) -> None:
        """Validate that all required templates exist."""
        required_templates = [
            'first_page.html',
            'deviation_statement.html',
            'extra_items.html',
            'note_sheet.html'
        ]
        
        for template in required_templates:
            template_path = self.template_dir / template
            if not template_path.exists():
                logger.warning(f"Template not found: {template_path}")
            else:
                logger.debug(f"Found template: {template_path}")
    
    def process_bill(self, input_file: str, output_dir: str) -> bool:
        """Process a bill from input file and generate output documents.
        
        Args:
            input_file: Path to the input Excel file
            output_dir: Directory to save generated documents
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            logger.info(f"Processing bill from {input_file}")
            
            # Ensure output directory exists
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # TODO: Implement bill processing logic
            # 1. Process Excel file
            # 2. Generate documents using templates
            # 3. Save outputs to output_dir
            
            logger.info(f"Bill processing completed. Output saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing bill: {e}", exc_info=True)
            return False

def main():
    """Main entry point for the Windsurf application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Windsurf Billing System')
    parser.add_argument('input', help='Input Excel file')
    parser.add_argument('-o', '--output', default='output', help='Output directory')
    parser.add_argument('--templates', help='Custom templates directory')
    
    args = parser.parse_args()
    
    app = WindsurfApp(template_dir=args.templates)
    success = app.process_bill(args.input, args.output)
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
