import os
import tempfile
import logging
from datetime import datetime
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Set up logging
logger = logging.getLogger(__name__)

class DocumentGeneratorV04:
    """
    V04 Document Generator for creating bill-related documents.
    
    This class handles the generation of various document types including:
    - First page
    - Deviation statements
    - Extra items
    - Certificates (II & III)
    - Note sheets
    
    It supports multiple output formats: HTML, PDF, and DOCX.
    """
    
    def __init__(self):
        """Initialize the document generator with default settings."""
        self.templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.output_dir = tempfile.mkdtemp(prefix='windsurf_output_')
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Generation flags
        self.generate_html = True
        self.generate_pdf = True
        self.generate_docx = True
        self.generate_latex = False
        
        logger.info(f"DocumentGeneratorV04 initialized. Output directory: {self.output_dir}")
    
    def generate_all_documents(self, data, reverse_font=False):
        """
        Generate all document types for the given data.
        
        Args:
            data (dict): The bill data to use for generation
            reverse_font (bool, optional): Whether to use reverse font colors. Defaults to False.
            
        Returns:
            list: Paths to all generated files
        """
        generated_files = []
        html_files = []
        
        try:
            # Generate HTML templates first
            if self.generate_html:
                html_files = self._generate_html_documents(data, reverse_font)
                generated_files.extend(html_files)
            
            # Generate PDF versions from HTML
            if self.generate_pdf and html_files:
                pdf_files = self._generate_pdf_documents(html_files)
                generated_files.extend(pdf_files)
            
            # Generate DOCX versions
            if self.generate_docx:
                docx_files = self._generate_docx_documents(data)
                generated_files.extend(docx_files)
            
            # Generate LaTeX versions if enabled
            if self.generate_latex:
                latex_files = self._generate_latex_documents(data)
                generated_files.extend(latex_files)
            
            logger.info(f"Generated {len(generated_files)} documents")
            return generated_files
            
        except Exception as e:
            logger.error(f"Error generating documents: {e}", exc_info=True)
            raise
    
    # [Previous implementation of all other methods from document_generator_v04.py]
    # Note: All methods from the original file should be included here
    # with updated imports and logging as needed
    
    # Example method (include all methods from the original file):
    def _generate_html_documents(self, data, reverse_font):
        """Generate all HTML documents."""
        html_files = []
        documents = {
            'first_page': 'first_page.html',
            'deviation_statement': 'deviation_statement.html',
            'extra_items': 'extra_items.html',
            'certificate_ii': 'certificate_ii.html',
            'certificate_iii': 'certificate_iii.html',
            'note_sheet': 'note_sheet.html',
            'bill_template': 'bill_template.html',
            'last_page': 'last_page.html'
        }
        
        for doc_type, template_name in documents.items():
            try:
                template_path = os.path.join(self.templates_dir, template_name)
                if not os.path.exists(template_path):
                    logger.warning(f"Template not found: {template_name}")
                    continue
                
                template = self.jinja_env.get_template(template_name)
                template_data = data.copy()
                
                # Template-specific data preparation
                if doc_type == 'deviation_statement':
                    if 'deviation_items' in data and data['deviation_items']:
                        template_data['items'] = data['deviation_items']
                    else:
                        template_data['items'] = self._convert_bill_items_to_deviation(data.get('items', []))
                elif doc_type == 'extra_items':
                    template_data['items'] = data.get('extra_items', [])
                
                # Render template
                html_content = template.render(
                    data=template_data,
                    reverse_font=reverse_font,
                    generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    items=template_data.get('items', []),
                    **{k: v for k, v in template_data.items() 
                       if k not in ['data', 'reverse_font', 'generation_date', 'items']}
                )
                
                # Save HTML file
                output_path = os.path.join(self.output_dir, f'{doc_type}.html')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                html_files.append(output_path)
                logger.info(f"Generated HTML: {doc_type}")
                
            except Exception as e:
                logger.error(f"Error generating {doc_type} HTML: {e}")
                continue
        
        return html_files
    
    # Include all other methods from document_generator_v04.py here
    # _generate_pdf_documents, _generate_docx_documents, _generate_latex_documents,
    # _convert_bill_items_to_deviation, _add_project_info, _add_bill_items_table, etc.
    
    # [End of document generator implementation]
