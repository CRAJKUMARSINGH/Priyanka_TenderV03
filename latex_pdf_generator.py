"""
Enhanced PDF Generator using LaTeX templates and HTML conversion
"""
import os
import json
from typing import Dict, List, Any
from weasyprint import HTML, CSS
from datetime import datetime
import tempfile

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
        
        print(f"Template not found: {template_name}")
        return ""
    
    def create_comparative_statement_html(self, work_data: Dict, bidders: List[Dict]) -> str:
        """Create HTML that matches the exact PWD comparative statement format"""
        if not bidders:
            return ""
        
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
    
    def generate_comparative_statement_pdf(self, work_data: Dict, bidders: List[Dict], output_path: str) -> bool:
        """Generate comparative statement PDF"""
        try:
            template = self.load_template("latex_code_for_comparative_statement")
            if not template:
                return False
            
            # Replace placeholders with actual data
            html_content = self._replace_comparative_placeholders(template, work_data, bidders)
            html_content = self.convert_latex_to_html(html_content)
            
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
            HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
            return True
            
        except Exception as e:
            print(f"Error generating comparative statement PDF: {e}")
            return False
    
    def generate_letter_acceptance_pdf(self, work_data: Dict, l1_bidder: Dict, output_path: str) -> bool:
        """Generate letter of acceptance PDF"""
        try:
            template = self.load_template("latex_code_for_letter_of_aceptance")
            if not template:
                return False
            
            # Replace placeholders
            html_content = self._replace_letter_placeholders(template, work_data, l1_bidder)
            html_content = self.convert_latex_to_html(html_content)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(output_path)
            return True
            
        except Exception as e:
            print(f"Error generating letter of acceptance PDF: {e}")
            return False
    
    def generate_work_order_pdf(self, work_data: Dict, l1_bidder: Dict, output_path: str) -> bool:
        """Generate work order PDF"""
        try:
            template = self.load_template("latex_code_for_work_order")
            if not template:
                return False
            
            # Replace placeholders
            html_content = self._replace_work_order_placeholders(template, work_data, l1_bidder)
            html_content = self.convert_latex_to_html(html_content)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(output_path)
            return True
            
        except Exception as e:
            print(f"Error generating work order PDF: {e}")
            return False
    
    def generate_scrutiny_sheet_pdf(self, work_data: Dict, bidders: List[Dict], output_path: str) -> bool:
        """Generate scrutiny sheet PDF"""
        try:
            template = self.load_template("latex_code_for_scrutiny_sheet")
            if not template:
                return False
            
            # Replace placeholders
            html_content = self._replace_scrutiny_placeholders(template, work_data, bidders)
            html_content = self.convert_latex_to_html(html_content)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(output_path)
            return True
            
        except Exception as e:
            print(f"Error generating scrutiny sheet PDF: {e}")
            return False
    
    def _replace_comparative_placeholders(self, template: str, work_data: Dict, bidders: List[Dict]) -> str:
        """Replace placeholders in comparative statement template"""
        if not bidders:
            return template
        
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
    
    def _replace_letter_placeholders(self, template: str, work_data: Dict, l1_bidder: Dict) -> str:
        """Replace placeholders in letter of acceptance template"""
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
    
    def _replace_work_order_placeholders(self, template: str, work_data: Dict, l1_bidder: Dict) -> str:
        """Replace placeholders in work order template"""
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
    
    def _replace_scrutiny_placeholders(self, template: str, work_data: Dict, bidders: List[Dict]) -> str:
        """Replace placeholders in scrutiny sheet template"""
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