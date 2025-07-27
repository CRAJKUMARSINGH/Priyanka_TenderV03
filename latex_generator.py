"""
LaTeX Generator for Tender Processing System
Handles LaTeX template processing and PDF compilation
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from date_utils import DateUtils

class LaTeXGenerator:
    """Generates PDF documents using LaTeX templates."""
    
    def __init__(self):
        self.date_utils = DateUtils()
        self.template_dir = Path("latex_templates")
        
        # Ensure template directory exists
        self.template_dir.mkdir(exist_ok=True)
        
        # Check if LaTeX is available
        self._check_latex_availability()
    
    def _check_latex_availability(self):
        """Check if LaTeX (pdflatex) is available on the system."""
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logging.info("LaTeX (pdflatex) is available")
            else:
                logging.warning("LaTeX may not be properly installed")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logging.error("LaTeX (pdflatex) not found. Please install TeX Live or MiKTeX")
    
    def generate_document(self, doc_type: str, work: Dict[str, Any], 
                         bidders: List[Dict[str, Any]]) -> Optional[bytes]:
        """Generate a PDF document of the specified type."""
        
        try:
            # Generate LaTeX content
            latex_content = self._generate_latex_content(doc_type, work, bidders)
            if not latex_content:
                logging.error(f"Failed to generate LaTeX content for {doc_type}")
                return None
            
            # Compile LaTeX to PDF
            pdf_data = self._compile_latex_to_pdf(latex_content)
            return pdf_data
            
        except Exception as e:
            logging.error(f"Error generating document {doc_type}: {e}")
            return None
    
    def _generate_latex_content(self, doc_type: str, work: Dict[str, Any], 
                               bidders: List[Dict[str, Any]]) -> Optional[str]:
        """Generate LaTeX content by substituting variables in templates."""
        
        template_file = self.template_dir / f"{doc_type}.tex"
        
        if not template_file.exists():
            logging.error(f"Template file not found: {template_file}")
            return None
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Prepare substitution variables
            variables = self._prepare_template_variables(work, bidders)
            
            # Substitute variables in template
            latex_content = self._substitute_variables(template_content, variables)
            
            return latex_content
            
        except Exception as e:
            logging.error(f"Error processing template {template_file}: {e}")
            return None
    
    def _prepare_template_variables(self, work: Dict[str, Any], 
                                   bidders: List[Dict[str, Any]]) -> Dict[str, str]:
        """Prepare variables for template substitution."""
        
        # Sort bidders by bid amount to get L1
        sorted_bidders = sorted(bidders, key=lambda x: x['bid_amount'])
        l1_bidder = sorted_bidders[0] if sorted_bidders else None
        
        # Parse dates
        original_date = work['work_info']['date']
        parsed_date = self.date_utils.parse_date(original_date)
        formatted_date = self.date_utils.format_display_date(parsed_date) if parsed_date else original_date
        
        # Calculate receipt date (assuming same as NIT date for now)
        receipt_date = formatted_date
        
        # Basic work information
        variables = {
            'WORK_NAME': self._latex_escape(work['work_name']),
            'NIT_NUMBER': self._latex_escape(work['nit_number']),
            'NIT_DATE': self._latex_escape(formatted_date),
            'RECEIPT_DATE': self._latex_escape(receipt_date),
            'ESTIMATED_COST': f"{float(work['work_info']['estimated_cost']):,.0f}",
            'EARNEST_MONEY': str(work['work_info']['earnest_money']),
            'TIME_COMPLETION': self._latex_escape(work['work_info']['time_of_completion']),
            'CURRENT_DATE': self._latex_escape(self.date_utils.get_current_date()),
            'NUM_TENDERS': str(len(bidders))
        }
        
        # L1 bidder information
        if l1_bidder:
            variables.update({
                'L1_BIDDER_NAME': self._latex_escape(l1_bidder['name']),
                'L1_BIDDER_CONTACT': self._latex_escape(l1_bidder.get('contact', '')),
                'L1_BID_AMOUNT': f"{l1_bidder['bid_amount']:,.0f}",
                'L1_PERCENTAGE': f"{l1_bidder['percentage']:+.2f}",
                'L1_PERCENTAGE_ABS': f"{abs(l1_bidder['percentage']):.2f}"
            })
        
        # Generate bidder table rows for comparative statement
        bidder_rows = []
        for i, bidder in enumerate(sorted_bidders):
            row = f"{i+1} & {self._latex_escape(bidder['name'])} & {float(work['work_info']['estimated_cost']):,.0f} & {bidder['percentage']:+.2f}\\% & {bidder['bid_amount']:,.0f} \\\\"
            bidder_rows.append(row)
        
        variables['BIDDER_TABLE_ROWS'] = '\n        '.join(bidder_rows)
        
        return variables
    
    def _substitute_variables(self, template_content: str, variables: Dict[str, str]) -> str:
        """Substitute variables in the template content."""
        
        content = template_content
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            content = content.replace(placeholder, str(var_value))
        
        return content
    
    def _latex_escape(self, text: str) -> str:
        """Escape special LaTeX characters in text."""
        if not isinstance(text, str):
            text = str(text)
        
        # Common LaTeX special characters
        escape_map = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '\\': '\\textbackslash{}'
        }
        
        for char, escaped in escape_map.items():
            text = text.replace(char, escaped)
        
        return text
    
    def _compile_latex_to_pdf(self, latex_content: str) -> Optional[bytes]:
        """Compile LaTeX content to PDF using pdflatex."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write LaTeX content to file
            tex_file = temp_path / "document.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            try:
                # Run pdflatex (twice for proper cross-references)
                for _ in range(2):
                    result = subprocess.run([
                        'pdflatex',
                        '-interaction=nonstopmode',
                        '-output-directory', str(temp_path),
                        str(tex_file)
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode != 0:
                        logging.error(f"LaTeX compilation failed: {result.stderr}")
                        # Try to extract useful error information
                        if "! LaTeX Error:" in result.stdout:
                            error_line = next((line for line in result.stdout.split('\n') 
                                             if "! LaTeX Error:" in line), "Unknown error")
                            logging.error(f"LaTeX Error: {error_line}")
                        return None
                
                # Read the generated PDF
                pdf_file = temp_path / "document.pdf"
                if pdf_file.exists():
                    with open(pdf_file, 'rb') as f:
                        pdf_data = f.read()
                    return pdf_data
                else:
                    logging.error("PDF file was not generated")
                    return None
                    
            except subprocess.TimeoutExpired:
                logging.error("LaTeX compilation timed out")
                return None
            except Exception as e:
                logging.error(f"Error during LaTeX compilation: {e}")
                return None
