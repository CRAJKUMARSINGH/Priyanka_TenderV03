import os
import tempfile
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import pdfkit
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import time
import zipfile

class WKHTMLTOPDFPool:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, pool_size=4):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_pool(pool_size)
        return cls._instance
    
    def _init_pool(self, pool_size):
        self.pool_size = pool_size
        self.available = Queue(maxsize=pool_size)
        self.in_use = set()
        self.lock = threading.Lock()
        
        # Pre-initialize wkhtmltopdf processes
        for _ in range(pool_size):
            self.available.put(pdfkit.PDFKit(
                'html',
                'string',
                options={
                    'page-size': 'A4',
                    'margin-top': '10mm',
                    'margin-right': '10mm',
                    'margin-bottom': '10mm',
                    'margin-left': '10mm',
                    'encoding': "UTF-8",
                    'no-outline': None,
                    'enable-local-file-access': None,
                    'quiet': ''
                }
            ))
    
    def acquire(self, timeout=30):
        """Acquire a wkhtmltopdf process from the pool"""
        try:
            wk = self.available.get(timeout=timeout)
            with self.lock:
                self.in_use.add(wk)
            return wk
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to acquire wkhtmltopdf process: {e}")
            raise
    
    def release(self, wk):
        """Release a wkhtmltopdf process back to the pool"""
        with self.lock:
            if wk in self.in_use:
                self.in_use.remove(wk)
                self.available.put(wk)

class DocumentGeneratorV04:
    """Generate V04 compliant documents from processed Excel data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates_dir = os.path.join(os.getcwd(), 'templates')
        self.output_dir = tempfile.mkdtemp(prefix='bill_v04_')
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Default generation flags
        self.generate_html = True
        self.generate_pdf = True
        self.generate_docx = True
        self.generate_latex = False
        
        # Initialize PDF generation pool (4 workers by default)
        self.pdf_pool = WKHTMLTOPDFPool(pool_size=4)
        self.pdf_timeout = 10  # seconds per PDF generation
    
    def generate_all_documents(self, data, reverse_font=False):
        """Generate all document types with optimized performance"""
        start_time = time.time()
        generated_files = []
        
        try:
            # Generate HTML in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                html_future = executor.submit(self._generate_html_documents, data, reverse_font)
                
                # Start other generations in parallel
                futures = {
                    'html': html_future
                }
                
                # Wait for HTML to be ready before starting PDF generation
                html_files = html_future.result()
                
                if self.generate_pdf and html_files:
                    futures['pdf'] = executor.submit(self._generate_pdf_documents, html_files)
                
                # Wait for all futures to complete
                for future in as_completed(futures.values()):
                    result = future.result()
                    if isinstance(result, list):
                        generated_files.extend(result)
            
            # Generate ZIP if we have files
            if generated_files:
                zip_path = self._generate_zip_archive(generated_files)
                if zip_path:
                    generated_files.append(zip_path)
            
            elapsed = time.time() - start_time
            self.logger.info(f"Generated {len(generated_files)} files in {elapsed:.2f} seconds")
            return generated_files
            
        except Exception as e:
            self.logger.error(f"Error in document generation: {e}")
            raise
    
    def _generate_html_documents(self, data, reverse_font):
        """Generate all HTML documents"""
        html_files = []
        
        # Document types to generate
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
                # Check if template exists
                template_path = os.path.join(self.templates_dir, template_name)
                if not os.path.exists(template_path):
                    self.logger.warning(f"Template not found: {template_name}")
                    continue
                
                # Load template
                template = self.jinja_env.get_template(template_name)
                
                # Prepare template-specific data
                template_data = data.copy()
                
                # For deviation statement, ensure items are properly structured
                if doc_type == 'deviation_statement':
                    if 'deviation_items' in data and data['deviation_items']:
                        template_data['items'] = data['deviation_items']
                    else:
                        template_data['items'] = self._convert_bill_items_to_deviation(
                            data.get('items', [])
                        )
                
                # For extra_items template, use extra_items data
                elif doc_type == 'extra_items':
                    template_data['items'] = data.get('extra_items', [])
                
                # Render with data
                render_args = {
                    'data': template_data,
                    'reverse_font': reverse_font,
                    'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'items': template_data.get('items', [])
                }
                # Add additional template data, avoiding duplicates
                for k, v in template_data.items():
                    if k not in ['data', 'reverse_font', 'generation_date', 'items']:
                        render_args[k] = v
                        
                html_content = template.render(**render_args)
                
                # Save HTML file
                output_path = os.path.join(self.output_dir, f'{doc_type}.html')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                html_files.append(output_path)
                self.logger.info(f"Generated HTML: {doc_type}")
                
            except Exception as e:
                self.logger.error(f"Error generating {doc_type} HTML: {e}")
                continue
        
        return html_files
    
    def _generate_pdf_documents(self, html_files):
        """Generate PDF documents from HTML files with robust error handling and process management"""
        if not html_files:
            self.logger.warning("No HTML files provided for PDF generation")
            return []

        pdf_files = []
        start_time = time.time()
        processes = []
        temp_files = []

        def cleanup():
            """Clean up any remaining processes and temporary files"""
            # Terminate any running processes
            for process in processes:
                try:
                    if process.poll() is None:  # Process is still running
                        process.terminate()
                        try:
                            process.wait(timeout=2)
                        except:
                            process.kill()
                except:
                    pass
            
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass

        try:
            # Process files sequentially to avoid resource exhaustion
            for html_path in html_files:
                try:
                    output_path = os.path.splitext(html_path)[0] + '.pdf'
                    
                    # Create a temporary file for the HTML content
                    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.html', delete=False) as f:
                        with open(html_path, 'rb') as src:
                            f.write(src.read())
                        temp_html = f.name
                        temp_files.append(temp_html)

                    # Prepare command
                    cmd = [
                        'wkhtmltopdf',
                        '--quiet',
                        '--enable-javascript',
                        '--javascript-delay', '1000',
                        '--no-stop-slow-scripts',
                        '--disable-smart-shrinking',
                        '--margin-top', '10mm',
                        '--margin-bottom', '10mm',
                        '--margin-left', '10mm',
                        '--margin-right', '10mm',
                        temp_html,
                        output_path
                    ]

                    # Start the process
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    processes.append(process)

                    # Wait with timeout
                    try:
                        stdout, stderr = process.communicate(timeout=self.pdf_timeout)
                        if process.returncode != 0:
                            error_msg = stderr.decode('utf-8', errors='replace')
                            self.logger.error(f"PDF generation failed for {html_path}: {error_msg}")
                            continue
                        
                        if os.path.exists(output_path):
                            pdf_files.append(output_path)
                            self.logger.info(f"Successfully generated PDF: {output_path}")
                        else:
                            self.logger.error(f"PDF was not created: {output_path}")
                            
                    except subprocess.TimeoutExpired:
                        process.kill()
                        self.logger.error(f"PDF generation timed out for {html_path}")
                        continue

                except Exception as e:
                    self.logger.error(f"Error processing {html_path}: {str(e)}")
                    continue

        finally:
            cleanup()

        elapsed = time.time() - start_time
        success_rate = (len(pdf_files) / len(html_files)) * 100 if html_files else 0
        self.logger.info(
            f"Generated {len(pdf_files)}/{len(html_files)} PDFs "
            f"(Success: {success_rate:.1f}%) in {elapsed:.2f} seconds"
        )
        
        return pdf_files
    
    def _generate_zip_archive(self, files, output_path=None):
        """Generate a ZIP archive of all generated files"""
        if not files:
            self.logger.warning("No files provided for ZIP archive")
            return None
            
        if output_path is None:
            output_path = os.path.join(self.output_dir, 'billing_documents.zip')
            
        start_time = time.time()
        
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if os.path.exists(file_path):
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
            
            elapsed = time.time() - start_time
            self.logger.info(f"Created ZIP archive with {len(files)} files in {elapsed:.2f} seconds")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating ZIP archive: {e}")
            return None
    
    def _convert_bill_items_to_deviation(self, items):
        """Convert regular bill items to deviation format"""
        deviation_items = []
        
        for item in items:
            deviation_item = {
                'description': item.get('description', 'Item'),
                'original_qty': item.get('quantity', '0'),
                'revised_qty': item.get('quantity', '0'),
                'difference': '0',
                'rate': item.get('rate', '0'),
                'amount': item.get('amount', '0')
            }
            deviation_items.append(deviation_item)
        
        return deviation_items
    
    def _add_project_info(self, doc, data):
        """Add project information to DOCX"""
        doc.add_heading('Project Information', level=1)
        
        info_table = doc.add_table(rows=4, cols=2)
        info_table.style = 'Table Grid'
        
        # Project details
        info_table.cell(0, 0).text = 'Project Name'
        info_table.cell(0, 1).text = data.get('project_name', 'N/A')
        
        info_table.cell(1, 0).text = 'Contractor'
        info_table.cell(1, 1).text = data.get('contractor_name', 'N/A')
        
        info_table.cell(2, 0).text = 'Bill Number'
        info_table.cell(2, 1).text = data.get('bill_number', 'N/A')
        
        info_table.cell(3, 0).text = 'Bill Date'
        info_table.cell(3, 1).text = data.get('bill_date', 'N/A')
    
    def _add_bill_items_table(self, doc, data):
        """Add bill items table to DOCX"""
        doc.add_heading('Bill Items', level=1)
        
        items = data.get('items', [])
        if not items:
            doc.add_paragraph("No items found in the bill.")
            return
        
        # Create table
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        
        # Header row
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Description'
        hdr_cells[1].text = 'Quantity'
        hdr_cells[2].text = 'Rate'
        hdr_cells[3].text = 'Amount'
        
        # Add items
        for item in items:
            row_cells = table.add_row().cells
            row_cells[0].text = item.get('description', '')
            row_cells[1].text = str(item.get('quantity', ''))
            row_cells[2].text = str(item.get('rate', ''))
            row_cells[3].text = str(item.get('amount', ''))
    
    def _add_certificate_ii_content(self, doc, data):
        """Add Certificate II content"""
        doc.add_heading('Certificate II - Quality Compliance', level=1)
        
        doc.add_paragraph("This certifies that:")
        doc.add_paragraph("• Work has been executed in accordance with approved drawings and specifications")
        doc.add_paragraph("• Work has been inspected and found to meet quality standards")
        doc.add_paragraph("• Work is completed as per contract requirements")
        
        doc.add_paragraph(f"\nProject: {data.get('project_name', 'N/A')}")
        doc.add_paragraph(f"Contractor: {data.get('contractor_name', 'N/A')}")
        doc.add_paragraph(f"Inspection Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        doc.add_paragraph("\n\nAuthorized Signature: ____________________")
        doc.add_paragraph("Quality Inspector")
    
    def _add_certificate_iii_content(self, doc, data):
        """Add Certificate III content"""
        doc.add_heading('Final Approval & Payment Authorization', level=1)
        
        doc.add_paragraph("This certifies that:")
        doc.add_paragraph("• All work has been completed satisfactorily")
        doc.add_paragraph("• Quality compliance certificate (Certificate II) has been verified")
        doc.add_paragraph("• Payment authorization is hereby granted")
        
        doc.add_paragraph(f"\nProject: {data.get('project_name', 'N/A')}")
        doc.add_paragraph(f"Contractor: {data.get('contractor_name', 'N/A')}")
        doc.add_paragraph(f"Total Amount: ₹ {self._calculate_total_amount(data)}")
        doc.add_paragraph(f"Authorization Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        doc.add_paragraph("\n\nAuthorized Signature: ____________________")
        doc.add_paragraph("Project Manager")
    
    def _create_latex_content(self, data):
        """Create LaTeX document content"""
        latex_template = r'''
\documentclass[a4paper,12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{booktabs}
\usepackage{longtable}

\title{Bill Document V04}
\author{''' + data.get('contractor_name', 'N/A') + r'''}
\date{''' + datetime.now().strftime('%Y-%m-%d') + r'''}

\begin{document}
\maketitle

\section{Project Information}
\begin{itemize}
\item Project Name: ''' + data.get('project_name', 'N/A') + r'''
\item Contractor: ''' + data.get('contractor_name', 'N/A') + r'''
\item Bill Number: ''' + data.get('bill_number', 'N/A') + r'''
\item Premium Percentage: ''' + str(data.get('premium_percentage', 0)) + r'''\%
\end{itemize}

\section{Certificate II - Quality Compliance}
This certifies that the work described in this bill has been executed in accordance with approved drawings and specifications, inspected and found to meet quality standards, and completed as per contract requirements.

\section{Certificate III - Final Approval}
This certifies that all work has been completed satisfactorily, quality compliance has been verified, and payment authorization is hereby granted.

\end{document}
'''
        return latex_template
    
    def _add_first_page_content(self, doc, data):
        """Add first page content to DOCX"""
        doc.add_heading('First Page - Bill Summary', level=1)
        
        # Project information
        self._add_project_info(doc, data)
        
        # Bill summary
        doc.add_heading('Bill Summary', level=2)
        doc.add_paragraph(f"Total Amount: ₹ {self._calculate_total_amount(data):,.2f}")
        doc.add_paragraph(f"Premium Percentage: {data.get('premium_percentage', 0)}%")
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _add_bill_template_content(self, doc, data):
        """Add bill template content to DOCX"""
        doc.add_heading('Bill Template', level=1)
        
        # Add project info and bill items
        self._add_project_info(doc, data)
        self._add_bill_items_table(doc, data)
    
    def _add_deviation_statement_content(self, doc, data):
        """Add deviation statement content to DOCX"""
        doc.add_heading('Deviation Statement', level=1)
        
        deviation_items = data.get('deviation_items', [])
        if not deviation_items:
            deviation_items = self._convert_bill_items_to_deviation(data.get('items', []))
        
        if deviation_items:
            # Create deviation table
            table = doc.add_table(rows=1, cols=5)
            table.style = 'Table Grid'
            
            # Header row
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'Description'
            hdr_cells[1].text = 'Original Qty'
            hdr_cells[2].text = 'Revised Qty'
            hdr_cells[3].text = 'Rate'
            hdr_cells[4].text = 'Amount'
            
            # Add deviation items
            for item in deviation_items:
                row_cells = table.add_row().cells
                row_cells[0].text = item.get('description', '')
                row_cells[1].text = str(item.get('original_qty', ''))
                row_cells[2].text = str(item.get('revised_qty', ''))
                row_cells[3].text = str(item.get('rate', ''))
                row_cells[4].text = str(item.get('amount', ''))
        else:
            doc.add_paragraph("No deviation items found.")
    
    def _add_extra_items_content(self, doc, data):
        """Add extra items content to DOCX"""
        doc.add_heading('Extra Items', level=1)
        
        extra_items = data.get('extra_items', [])
        if extra_items:
            # Create extra items table
            table = doc.add_table(rows=1, cols=4)
            table.style = 'Table Grid'
            
            # Header row
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'Description'
            hdr_cells[1].text = 'Quantity'
            hdr_cells[2].text = 'Rate'
            hdr_cells[3].text = 'Amount'
            
            # Add extra items
            for item in extra_items:
                row_cells = table.add_row().cells
                row_cells[0].text = item.get('description', '')
                row_cells[1].text = str(item.get('quantity', ''))
                row_cells[2].text = str(item.get('rate', ''))
                row_cells[3].text = str(item.get('amount', ''))
        else:
            doc.add_paragraph("No extra items found.")
    
    def _add_note_sheet_content(self, doc, data):
        """Add note sheet content to DOCX"""
        doc.add_heading('Note Sheet', level=1)
        
        doc.add_paragraph("Important Notes:")
        doc.add_paragraph("• All quantities and rates have been verified")
        doc.add_paragraph("• Work completed as per specifications")
        doc.add_paragraph("• Quality standards maintained throughout")
        
        doc.add_paragraph(f"\nBill prepared on: {datetime.now().strftime('%Y-%m-%d')}")
        doc.add_paragraph(f"Project: {data.get('project_name', 'N/A')}")
        
        # Add any additional notes from data
        if 'notes' in data and data['notes']:
            doc.add_paragraph(f"\nAdditional Notes: {data['notes']}")
    
    def _add_last_page_content(self, doc, data):
        """Add last page content to DOCX"""
        doc.add_heading('Last Page - Final Summary', level=1)
        
        # Final totals
        doc.add_paragraph("FINAL SUMMARY")
        doc.add_paragraph(f"Total Amount: ₹ {self._calculate_total_amount(data):,.2f}")
        doc.add_paragraph(f"Premium Applied: {data.get('premium_percentage', 0)}%")
        
        # Signature sections
        doc.add_paragraph("\n\nContractor Signature: ____________________")
        doc.add_paragraph("Date: ____________________")
        doc.add_paragraph("\n\nAuthorizing Officer: ____________________")
        doc.add_paragraph("Date: ____________________")

    def _calculate_total_amount(self, data):
        """Calculate total bill amount"""
        total = 0.0
        
        # Calculate from bill summary
        if 'bill_summary' in data and hasattr(data['bill_summary'], 'sum'):
            df = data['bill_summary']
            # Look for amount columns
            amount_cols = [col for col in df.columns if 'amount' in str(col).lower()]
            for col in amount_cols:
                try:
                    total += df[col].sum()
                except:
                    pass
        
        # Add premium
        premium_pct = data.get('premium_percentage', 0)
        total_with_premium = total * (1 + premium_pct/100)
        
        return total_with_premium
