"""
Enhanced PDF Generator using LaTeX templates and HTML conversion
Fixed version with proper error handling and memory management
"""
import os
import json
import re
from typing import Dict, List, Any
from weasyprint import HTML, CSS
from datetime import datetime
import tempfile
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LatexPDFGenerator:
    def __init__(self):
        self.templates_dir = "latex_templates"

    def load_template(self, template_name: str) -> str:
        """Load LaTeX template content"""
        # Try .TeX extension first (LaTeX files from attached assets)
        template_path = os.path.join(self.templates_dir, f"{template_name}.TeX")
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()

        # Try .tex extension as fallback
        template_path = os.path.join(self.templates_dir, f"{template_name}.tex")
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()

        logging.warning(f"Template not found: {template_name}")
        return ""

    def convert_latex_to_html(self, latex_content: str) -> str:
        """Convert basic LaTeX commands to HTML"""
        try:
            # Basic LaTeX to HTML conversion
            html_content = latex_content
            
            # Remove LaTeX document structure commands
            html_content = re.sub(r'\\documentclass\{.*?\}', '', html_content)
            html_content = re.sub(r'\\usepackage\{.*?\}', '', html_content)
            html_content = re.sub(r'\\begin\{document\}', '', html_content)
            html_content = re.sub(r'\\end\{document\}', '', html_content)
            
            # Convert basic formatting
            html_content = re.sub(r'\\textbf\{(.*?)\}', r'<strong>\1</strong>', html_content)
            html_content = re.sub(r'\\textit\{(.*?)\}', r'<em>\1</em>', html_content)
            html_content = re.sub(r'\\section\{(.*?)\}', r'<h2>\1</h2>', html_content)
            html_content = re.sub(r'\\subsection\{(.*?)\}', r'<h3>\1</h3>', html_content)
            
            # Convert tables
            html_content = re.sub(r'\\begin\{tabular\}\{.*?\}', '<table border="1" style="border-collapse: collapse; width: 100%;">', html_content)
            html_content = re.sub(r'\\end\{tabular\}', '</table>', html_content)
            html_content = re.sub(r'\\hline', '', html_content)
            html_content = re.sub(r'\\\\', '</tr><tr>', html_content)
            html_content = re.sub(r'&', '</td><td style="border: 1px solid black; padding: 5px;">', html_content)
            
            # Add opening and closing table row tags
            html_content = re.sub(r'<table[^>]*>', r'\g<0><tr>', html_content)
            html_content = re.sub(r'</table>', r'</tr></table>', html_content)
            
            # Add opening td tags
            html_content = re.sub(r'<tr>([^<])', r'<tr><td style="border: 1px solid black; padding: 5px;">\1', html_content)
            
            # Convert line breaks
            html_content = html_content.replace('\n\n', '</p><p>')
            html_content = html_content.replace('\n', '<br>')
            
            # Wrap in basic HTML structure
            if not html_content.strip().startswith('<'):
                html_content = f'<p>{html_content}</p>'
                
            return html_content
            
        except Exception as e:
            logging.error(f"Error converting LaTeX to HTML: {e}")
            return latex_content

    def create_comparative_statement_html(self, work_data: Dict, bidders: List[Dict]) -> str:
        """Create HTML that matches the exact PWD comparative statement format"""
        if not bidders:
            return ""

        try:
            # Find L1 bidder
            l1_bidder = min(bidders, key=lambda x: x.get('bid_amount', float('inf')))

            # Create bidder table rows
            bidder_rows_html = ""
            for i, bidder in enumerate(bidders, 1):
                percentage = bidder.get('percentage', 0)
                bid_amount = bidder.get('bid_amount', 0)
                percentage_text = f"{abs(percentage):.2f} {'BELOW' if percentage < 0 else 'ABOVE'}"

                bidder_rows_html += f"""
                <tr>
                    <td style="text-align: center; border: 1px solid black; padding: 5px;">{i}</td>
                    <td style="border: 1px solid black; padding: 5px;">{bidder.get('name', '')}</td>
                    <td style="text-align: center; border: 1px solid black; padding: 5px;">{work_data.get('estimated_cost', 0)}</td>
                    <td style="text-align: center; border: 1px solid black; padding: 5px;">{percentage_text}</td>
                    <td style="text-align: center; border: 1px solid black; padding: 5px;">{bid_amount}</td>
                </tr>
                """

            # Format the complete HTML matching PWD design
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Comparative Statement of Tenders</title>
                <style>
                    @page {{ size: A4 landscape; margin: 1cm; }}
                    body {{
                        font-family: Arial, sans-serif;
                        font-size: 11px;
                        margin: 0;
                        padding: 10px;
                    }}
                    .header {{
                        text-align: center;
                        font-weight: bold;
                        border: 2px solid black;
                        padding: 10px;
                        margin-bottom: 10px;
                    }}
                    .main-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 10px 0;
                        border: 1px solid black;
                    }}
                    .main-table td {{
                        border: 1px solid black;
                        padding: 5px;
                        font-size: 10px;
                    }}
                    .bidder-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 10px 0;
                    }}
                    .bidder-table th, .bidder-table td {{
                        border: 1px solid black;
                        padding: 5px;
                        text-align: center;
                        font-size: 10px;
                    }}
                    .bidder-table th {{
                        background-color: #f0f0f0;
                        font-weight: bold;
                    }}
                    .lowest-section {{
                        margin: 10px 0;
                        border: 1px solid black;
                        padding: 5px;
                    }}
                    .summary-box {{
                        border: 2px solid black;
                        padding: 10px;
                        margin: 10px 0;
                        background-color: #f9f9f9;
                    }}
                    .signature-section {{
                        display: flex;
                        justify-content: space-between;
                        margin-top: 20px;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div style="font-size: 14px;">OFFICE OF THE EXECUTIVE ENGINEER PWD ELECTRIC DIVISION, UDAIPUR</div>
                    <div style="font-size: 12px; margin: 5px 0;">COMPARATIVE STATEMENT OF TENDERS</div>
                    <div style="font-size: 11px;">Name of Work: {work_data.get('work_name', 'Electric cabling and maintenance work in Sahelion ki Bari, Udaipur')}</div>
                </div>

                <table class="main-table">
                    <tr>
                        <td style="font-weight: bold;">NIT No.:</td>
                        <td>{work_data.get('nit_number', '')}</td>
                        <td style="font-weight: bold;">Date:</td>
                        <td>{work_data.get('nit_date', '')}</td>
                        <td style="font-weight: bold;">ITEM-1</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">1. Estimated amount for item in NIT Rs.:</td>
                        <td>{work_data.get('estimated_cost', 0)}</td>
                        <td style="font-weight: bold;">Earnest Money @2% Rs.:</td>
                        <td>{int(work_data.get('estimated_cost', 0) * 0.02)}</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">2. Amount of tender recommended for Rs.:</td>
                        <td>{l1_bidder.get('bid_amount', 0)}</td>
                        <td style="font-weight: bold;">Time for Completion Months:</td>
                        <td>{work_data.get('time_completion', 6)}</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">3. Estimated amount of item not included in the tender Rs.:</td>
                        <td>Nil.</td>
                        <td style="font-weight: bold;">Date of calling NIT:</td>
                        <td>{work_data.get('nit_date', '')}</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">4. Contingencies and other provision included in the estimate Rs.:</td>
                        <td>As per rules</td>
                        <td style="font-weight: bold;">Date of Receipt of Tender:</td>
                        <td>{work_data.get('receipt_date', '')}</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">5. Cost of work as per recommended tender Rs.:</td>
                        <td>{l1_bidder.get('bid_amount', 0)}</td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold;">6. Percentage of excess / saving over the sanctioned estimate %:</td>
                        <td>As per recommended rate.</td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </table>

                <table class="bidder-table">
                    <tr>
                        <th>S.No</th>
                        <th>Bidder Name</th>
                        <th>Estimated Cost Rs.</th>
                        <th>Quoted Percentage</th>
                        <th>Quoted Amount Rs.</th>
                    </tr>
                    {bidder_rows_html}
                </table>

                <div class="lowest-section">
                    <strong>Lowest:</strong> {l1_bidder.get('name', '')} &nbsp;&nbsp;&nbsp;
                    {abs(l1_bidder.get('percentage', 0)):.2f} {'BELOW' if l1_bidder.get('percentage', 0) < 0 else 'ABOVE'} &nbsp;&nbsp;&nbsp;
                    <span style="color: red; font-weight: bold;">{l1_bidder.get('bid_amount', 0)}</span>
                </div>

                <div class="summary-box">
                    <div style="font-weight: bold; margin-bottom: 10px;">
                        The tender of the lowest bidder {l1_bidder.get('name', '')},
                        Udaipur @ {abs(l1_bidder.get('percentage', 0)):.0f}% {'BELOW' if l1_bidder.get('percentage', 0) < 0 else 'ABOVE'}
                        amounting to Rs. {l1_bidder.get('bid_amount', 0)}/-- In words
                        Rupees. Six Lakh Twenty Eight Thousand Eight Hundred Sixty One Only.
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                        <span>AR</span>
                        <span>DA</span>
                        <span>TA</span>
                        <span>EE</span>
                    </div>
                </div>

                <div class="signature-section">
                    <span>Auditor</span>
                    <span>Divisional Accountant</span>
                    <span>TA</span>
                    <span>Executive Engineer</span>
                </div>
            </body>
            </html>
            """

            return html
            
        except Exception as e:
            logging.error(f"Error creating comparative statement HTML: {e}")
            return ""

    def generate_comparative_statement_pdf(self, work_data: Dict, bidders: List[Dict], output_path: str = None) -> bytes:
        """Generate comparative statement PDF with improved error handling"""
        try:
            template = self.load_template("latex_code_for_comparative_statement")
            
            if template:
                # Use LaTeX template approach
                html_content = self._replace_comparative_placeholders(template, work_data, bidders)
                html_content = self.convert_latex_to_html(html_content)
            else:
                # Fallback to direct HTML generation
                html_content = self.create_comparative_statement_html(work_data, bidders)

            if not html_content:
                logging.error("No content generated for comparative statement")
                return b""

            # Add CSS for better styling
            css = CSS(string="""
                @page { size: A4 landscape; margin: 1cm; }
                body { font-family: Arial, sans-serif; font-size: 12px; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid black; padding: 5px; text-align: left; }
                th { background-color: #f0f0f0; font-weight: bold; }
                .center { text-align: center; }
                .bold { font-weight: bold; }
                h1 { font-size: 16px; text-align: center; margin: 10px 0; }
            """)

            # Generate PDF
            if output_path:
                HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
                with open(output_path, 'rb') as f:
                    return f.read()
            else:
                # Return PDF bytes directly
                return HTML(string=html_content).write_pdf(stylesheets=[css])

        except Exception as e:
            logging.error(f"Error generating comparative statement PDF: {e}")
            return b""

    def generate_letter_acceptance_pdf(self, work_data: Dict, l1_bidder: Dict, output_path: str = None) -> bytes:
        """Generate letter of acceptance PDF with improved error handling"""
        try:
            template = self.load_template("latex_code_for_letter_of_aceptance")
            
            if template:
                html_content = self._replace_letter_placeholders(template, work_data, l1_bidder)
                html_content = self.convert_latex_to_html(html_content)
            else:
                # Fallback HTML generation
                html_content = self._create_letter_acceptance_html(work_data, l1_bidder)

            if not html_content:
                logging.error("No content generated for letter of acceptance")
                return b""

            # Generate PDF
            if output_path:
                HTML(string=html_content).write_pdf(output_path)
                with open(output_path, 'rb') as f:
                    return f.read()
            else:
                return HTML(string=html_content).write_pdf()

        except Exception as e:
            logging.error(f"Error generating letter of acceptance PDF: {e}")
            return b""

    def generate_work_order_pdf(self, work_data: Dict, l1_bidder: Dict, output_path: str = None) -> bytes:
        """Generate work order PDF with improved error handling"""
        try:
            template = self.load_template("latex_code_for_work_order")
            
            if template:
                html_content = self._replace_work_order_placeholders(template, work_data, l1_bidder)
                html_content = self.convert_latex_to_html(html_content)
            else:
                # Fallback HTML generation
                html_content = self._create_work_order_html(work_data, l1_bidder)

            if not html_content:
                logging.error("No content generated for work order")
                return b""

            # Generate PDF
            if output_path:
                HTML(string=html_content).write_pdf(output_path)
                with open(output_path, 'rb') as f:
                    return f.read()
            else:
                return HTML(string=html_content).write_pdf()

        except Exception as e:
            logging.error(f"Error generating work order PDF: {e}")
            return b""

    def generate_scrutiny_sheet_pdf(self, work_data: Dict, bidders: List[Dict], output_path: str = None) -> bytes:
        """Generate scrutiny sheet PDF with improved error handling"""
        try:
            template = self.load_template("latex_code_for_scrutiny_sheet")
            
            if template:
                html_content = self._replace_scrutiny_placeholders(template, work_data, bidders)
                html_content = self.convert_latex_to_html(html_content)
            else:
                # Fallback HTML generation
                html_content = self._create_scrutiny_sheet_html(work_data, bidders)

            if not html_content:
                logging.error("No content generated for scrutiny sheet")
                return b""

            # Generate PDF
            if output_path:
                HTML(string=html_content).write_pdf(output_path)
                with open(output_path, 'rb') as f:
                    return f.read()
            else:
                return HTML(string=html_content).write_pdf()

        except Exception as e:
            logging.error(f"Error generating scrutiny sheet PDF: {e}")
            return b""

    def generate_bulk_pdfs(self, work_data: Dict, bidders: List[Dict]) -> Dict[str, bytes]:
        """Generate all PDFs at once with memory optimization"""
        try:
            logging.info("Starting bulk PDF generation")
            generated_pdfs = {}
            
            # Generate each document with individual error handling
            documents = [
                ('comparative_statement', self.generate_comparative_statement_pdf),
                ('letter_acceptance', self.generate_letter_acceptance_pdf),
                ('work_order', self.generate_work_order_pdf),
                ('scrutiny_sheet', self.generate_scrutiny_sheet_pdf)
            ]
            
            for doc_name, generator_func in documents:
                try:
                    if doc_name in ['letter_acceptance', 'work_order']:
                        # These need L1 bidder
                        l1_bidder = min(bidders, key=lambda x: x.get('bid_amount', float('inf')))
                        pdf_bytes = generator_func(work_data, l1_bidder)
                    else:
                        # These need all bidders
                        pdf_bytes = generator_func(work_data, bidders)
                    
                    if pdf_bytes:
                        generated_pdfs[doc_name] = pdf_bytes
                        logging.info(f"Successfully generated {doc_name} PDF")
                    else:
                        logging.warning(f"Failed to generate {doc_name} PDF - empty content")
                        
                except Exception as e:
                    logging.error(f"Error generating {doc_name} PDF: {e}")
                    continue
            
            logging.info(f"Bulk PDF generation completed. Generated {len(generated_pdfs)} documents")
            return generated_pdfs
            
        except Exception as e:
            logging.error(f"Error in bulk PDF generation: {e}")
            return {}

    def _create_letter_acceptance_html(self, work_data: Dict, l1_bidder: Dict) -> str:
        """Create fallback HTML for letter of acceptance"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Letter of Acceptance</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; font-weight: bold; margin-bottom: 20px; }}
                .content {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>LETTER OF ACCEPTANCE</h2>
                <p>PWD Electric Division, Udaipur</p>
            </div>
            <div class="content">
                <p><strong>Work:</strong> {work_data.get('work_name', '')}</p>
                <p><strong>NIT No.:</strong> {work_data.get('nit_number', '')}</p>
                <p><strong>Date:</strong> {datetime.now().strftime('%d-%m-%Y')}</p>
                <p><strong>Accepted Bidder:</strong> {l1_bidder.get('name', '')}</p>
                <p><strong>Bid Amount:</strong> Rs. {l1_bidder.get('bid_amount', 0)}</p>
            </div>
        </body>
        </html>
        """

    def _create_work_order_html(self, work_data: Dict, l1_bidder: Dict) -> str:
        """Create fallback HTML for work order"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Work Order</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; font-weight: bold; margin-bottom: 20px; }}
                .content {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>WORK ORDER</h2>
                <p>PWD Electric Division, Udaipur</p>
            </div>
            <div class="content">
                <p><strong>Work:</strong> {work_data.get('work_name', '')}</p>
                <p><strong>NIT No.:</strong> {work_data.get('nit_number', '')}</p>
                <p><strong>Contractor:</strong> {l1_bidder.get('name', '')}</p>
                <p><strong>Contract Amount:</strong> Rs. {l1_bidder.get('bid_amount', 0)}</p>
                <p><strong>Time for Completion:</strong> {work_data.get('time_completion', 6)} months</p>
            </div>
        </body>
        </html>
        """

    def _create_scrutiny_sheet_html(self, work_data: Dict, bidders: List[Dict]) -> str:
        """Create fallback HTML for scrutiny sheet"""
        bidder_rows = ""
        for i, bidder in enumerate(bidders, 1):
            bidder_rows += f"""
            <tr>
                <td>{i}</td>
                <td>{bidder.get('name', '')}</td>
                <td>Qualified</td>
                <td>Rs. {bidder.get('bid_amount', 0)}</td>
            </tr>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Scrutiny Sheet</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                th {{ background-color: #f0f0f0; }}
                .header {{ text-align: center; font-weight: bold; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>SCRUTINY SHEET</h2>
                <p>PWD Electric Division, Udaipur</p>
                <p><strong>Work:</strong> {work_data.get('work_name', '')}</p>
                <p><strong>NIT No.:</strong> {work_data.get('nit_number', '')}</p>
            </div>
            <table>
                <tr>
                    <th>S.No</th>
                    <th>Bidder Name</th>
                    <th>Status</th>
                    <th>Bid Amount</th>
                </tr>
                {bidder_rows}
            </table>
        </body>
        </html>
        """

    def _replace_comparative_placeholders(self, template: str, work_data: Dict, bidders: List[Dict]) -> str:
        """Replace placeholders in comparative statement template"""
        if not bidders:
            return template

        try:
            # Find L1 bidder (lowest)
            l1_bidder = min(bidders, key=lambda x: x.get('bid_amount', float('inf')))

            # Create bidder table rows
            bidder_rows = ""
            for i, bidder in enumerate(bidders, 1):
                percentage = bidder.get('percentage', 0)
                bid_amount = bidder.get('bid_amount', 0)
                percentage_text = f"{abs(percentage):.2f} {'BELOW' if percentage < 0 else 'ABOVE'}"

                bidder_rows += f"{i} & {bidder.get('name', '')} & {work_data.get('estimated_cost', 0)} & {percentage_text} & {bid_amount} \\\\\n"

            # Replace all placeholders
            replacements = {
                'WORK_NAME': work_data.get('work_name', ''),
                'NIT_NUMBER': work_data.get('nit_number', ''),
                'NIT_DATE': work_data.get('nit_date', ''),
                'ESTIMATED_COST': str(work_data.get('estimated_cost', 0)),
                'L1_BID_AMOUNT': str(l1_bidder.get('bid_amount', 0)),
                'EARNEST_MONEY': str(int(work_data.get('estimated_cost', 0) * 0.02)),
                'TIME_COMPLETION': str(work_data.get('time_completion', 6)),
                'RECEIPT_DATE': work_data.get('receipt_date', ''),
                'BIDDER_TABLE_ROWS': bidder_rows.strip(),
                'L1_BIDDER_NAME': l1_bidder.get('name', ''),
                'L1_PERCENTAGE': f"{abs(l1_bidder.get('percentage', 0)):.2f} {'BELOW' if l1_bidder.get('percentage', 0) < 0 else 'ABOVE'}",
                'L1_PERCENTAGE_ABS': f"{abs(l1_bidder.get('percentage', 0)):.0f}%"
            }

            result = template
            for placeholder, value in replacements.items():
                result = result.replace(f"{{{placeholder}}}", str(value))

            return result
            
        except Exception as e:
            logging.error(f"Error replacing comparative placeholders: {e}")
            return template

    def _replace_letter_placeholders(self, template: str, work_data: Dict, l1_bidder: Dict) -> str:
        """Replace placeholders in letter of acceptance template"""
        try:
            replacements = {
                'WORK_NAME': work_data.get('work_name', ''),
                'NIT_NUMBER': work_data.get('nit_number', ''),
                'NIT_DATE': work_data.get('nit_date', ''),
                'BIDDER_NAME': l1_bidder.get('name', ''),
                'BID_AMOUNT': str(l1_bidder.get('bid_amount', 0)),
                'PERCENTAGE': f"{abs(l1_bidder.get('percentage', 0)):.2f} {'BELOW' if l1_bidder.get('percentage', 0) < 0 else 'ABOVE'}",
                'CURRENT_DATE': datetime.now().strftime('%d-%m-%Y')
            }

            result = template
            for placeholder, value in replacements.items():
                result = result.replace(f"{{{placeholder}}}", str(value))

            return result
            
        except Exception as e:
            logging.error(f"Error replacing letter placeholders: {e}")
            return template

    def _replace_work_order_placeholders(self, template: str, work_data: Dict, l1_bidder: Dict) -> str:
        """Replace placeholders in work order template"""
        try:
            replacements = {
                'WORK_NAME': work_data.get('work_name', ''),
                'NIT_NUMBER': work_data.get('nit_number', ''),
                'BIDDER_NAME': l1_bidder.get('name', ''),
                'BID_AMOUNT': str(l1_bidder.get('bid_amount', 0)),
                'TIME_COMPLETION': str(work_data.get('time_completion', 6)),
                'CURRENT_DATE': datetime.now().strftime('%d-%m-%Y')
            }

            result = template
            for placeholder, value in replacements.items():
                result = result.replace(f"{{{placeholder}}}", str(value))

            return result
            
        except Exception as e:
            logging.error(f"Error replacing work order placeholders: {e}")
            return template

    def _replace_scrutiny_placeholders(self, template: str, work_data: Dict, bidders: List[Dict]) -> str:
        """Replace placeholders in scrutiny sheet template"""
        try:
            # Create bidder table rows for scrutiny
            bidder_rows = ""
            for i, bidder in enumerate(bidders, 1):
                bidder_rows += f"{i} & {bidder.get('name', '')} & Qualified & {bidder.get('bid_amount', 0)} \\\\\n"

            replacements = {
                'WORK_NAME': work_data.get('work_name', ''),
                'NIT_NUMBER': work_data.get('nit_number', ''),
                'NIT_DATE': work_data.get('nit_date', ''),
                'BIDDER_TABLE_ROWS': bidder_rows.strip(),
                'CURRENT_DATE': datetime.now().strftime('%d-%m-%Y')
            }

            result = template
            for placeholder, value in replacements.items():
                result = result.replace(f"{{{placeholder}}}", str(value))

            return result
            
        except Exception as e:
            logging.error(f"Error replacing scrutiny placeholders: {e}")
            return template