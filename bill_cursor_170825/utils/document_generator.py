import os
from typing import Dict, List, Any
import pandas as pd
from jinja2 import Environment, FileSystemLoader, Template, StrictUndefined
import streamlit as st
from datetime import datetime

class DocumentGenerator:
    """
    Utility class for generating HTML documents from processed Excel data.
    Uses Jinja2 templates for professional document formatting.
    """
    
    def __init__(self):
        self.template_dir = os.path.abspath("templates/html")
        
        # Document templates mapping
        self.document_templates = {
            'first_page': 'first_page.html',
            'deviation_statement': 'deviation_statement.html', 
            'note_sheet': 'note_sheet.html',
            'extra_items': 'extra_items.html',
            'certificate_ii': 'certificate_ii.html',
            'certificate_iii': 'certificate_iii.html'
        }
        
        # Ensure template directory exists
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Verify all required templates exist
        self._verify_templates()
        
        # Initialize Jinja2 environment with strict undefined to catch missing variables
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            undefined=StrictUndefined  # This will raise an error for undefined variables
        )
        
        # Add custom filters
        self.env.filters['format_currency'] = self._format_currency
        self.env.filters['format_date'] = self._format_date
        
    def _verify_templates(self):
        """Verify that all required template files exist."""
        missing_templates = []
        for name, filename in self.document_templates.items():
            template_path = os.path.join(self.template_dir, filename)
            if not os.path.exists(template_path):
                missing_templates.append(filename)
                
        if missing_templates:
            raise FileNotFoundError(
                f"Missing required template files: {', '.join(missing_templates)}. "
                f"Please ensure all templates are present in {self.template_dir}"
            )
    
    def generate_all_documents(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all required billing documents from the processed data.
        
        Args:
            data: Processed data from ExcelProcessor
            
        Returns:
            Dictionary with document names as keys and HTML content as values
        """
        documents = {}
        
        try:
            # Generate each document type
            for doc_name, template_name in self.document_templates.items():
                try:
                    html_content = self._generate_document(doc_name, template_name, data)
                    if html_content:
                        documents[doc_name] = html_content
                except Exception as e:
                    st.warning(f"⚠️ Could not generate {doc_name}: {str(e)}")
                    continue
            
            return documents
            
        except Exception as e:
            st.error(f"❌ Error generating documents: {str(e)}")
            return {}
    
    def _generate_document(self, doc_name: str, template_name: str, data: Dict[str, Any]) -> str:
        """
        Generate a single document from a template.
        
        Args:
            doc_name: Name of the document (for logging)
            template_name: Name of the template file
            data: Data to render in the template
            
        Returns:
            Rendered HTML content as string
        """
        try:
            # Get the template
            template = self.env.get_template(template_name)
            
            # Add common template variables
            template_vars = {
                'data': data,
                'now': datetime.now(),
                'version': '1.0.0'  # You can make this dynamic
            }
            
            # Render the template with the data
            return template.render(**template_vars)
            
        except Exception as e:
            error_msg = f"Error generating {doc_name} from template {template_name}: {str(e)}"
            st.error(error_msg)
            # Return an error message that will be visible in the output
            return f"<div style='color: red; padding: 1em; border: 1px solid red;'>{error_msg}</div>"
    
    def _prepare_template_data(self, doc_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and format data specifically for each document template."""
        
        # Base data that all templates need
        template_data = {
            'agreement_no': data.get('agreement_no', 'N/A'),
            'name_of_work': data.get('name_of_work', 'N/A'),
            'name_of_firm': data.get('name_of_firm', 'N/A'),
            'date_commencement': data.get('date_commencement', 'N/A'),
            'date_completion': data.get('date_completion', 'N/A'),
            'actual_completion': data.get('actual_completion', 'N/A'),
            'bill_items': data.get('bill_items', []),
            'extra_items': data.get('extra_items', []),
            'bill_total': data.get('bill_total', 0.0),
            'extra_items_total': data.get('extra_items_total', 0.0),
            'tender_premium_percent': data.get('tender_premium_percent', 0.10),
            'bill_premium': data.get('bill_premium', 0.0),
            'extra_premium': data.get('extra_premium', 0.0),
            'bill_grand_total': data.get('bill_grand_total', 0.0),
            'extra_items_sum': data.get('extra_items_sum', 0.0),
            'total_amount': data.get('total_amount', 0.0),
            'header': data.get('header', []),
            'generation_date': datetime.now().strftime('%B %d, %Y'),
            'generation_time': datetime.now().strftime('%I:%M %p')
        }
        
        # Document-specific data preparation
        if doc_name == 'first_page':
            template_data.update(self._prepare_first_page_data(data))
        elif doc_name == 'deviation_statement':
            template_data.update(self._prepare_deviation_data(data))
        elif doc_name == 'note_sheet':
            template_data.update(self._prepare_note_sheet_data(data))
        elif doc_name == 'extra_items':
            template_data.update(self._prepare_extra_items_data(data))
        elif doc_name in ['certificate_ii', 'certificate_iii']:
            template_data.update(self._prepare_certificate_data(data))
        
        return template_data
    
    def _prepare_first_page_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data specifically for the first page summary."""
        return {
            'extra_items_base': data.get('extra_items_total', 0.0),
            'page_title': 'First Page Summary',
            'document_type': 'Contractor Bill Summary'
        }
    
    def _prepare_deviation_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for deviation statement."""
        
        # Calculate deviations between work order and bill quantities
        deviations = []
        work_order_items = data.get('work_order_items', [])
        bill_items = data.get('bill_items', [])
        
        # Create a mapping of work order items by item number
        wo_map = {item.get('item_no', ''): item for item in work_order_items}
        
        for bill_item in bill_items:
            item_no = bill_item.get('item_no', '')
            wo_item = wo_map.get(item_no, {})
            
            wo_qty = wo_item.get('quantity', 0.0)
            bill_qty = bill_item.get('quantity_bill', 0.0)
            deviation_qty = bill_qty - wo_qty
            deviation_percent = (deviation_qty / wo_qty * 100) if wo_qty > 0 else 0
            
            if abs(deviation_qty) > 0.01:  # Only include meaningful deviations
                deviations.append({
                    'item_no': item_no,
                    'description': bill_item.get('description', ''),
                    'work_order_qty': wo_qty,
                    'bill_qty': bill_qty,
                    'deviation_qty': deviation_qty,
                    'deviation_percent': deviation_percent,
                    'unit': bill_item.get('unit', ''),
                    'rate': bill_item.get('rate', 0.0),
                    'amount_difference': deviation_qty * bill_item.get('rate', 0.0)
                })
        
        return {
            'deviations': deviations,
            'total_deviation_amount': sum(d['amount_difference'] for d in deviations),
            'page_title': 'Deviation Statement',
            'document_type': 'Work Order vs Bill Quantity Comparison'
        }
    
    def _prepare_note_sheet_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for note sheet (bill scrutiny)."""
        return {
            'page_title': 'Final Bill Scrutiny Sheet',
            'document_type': 'Bill Scrutiny and Verification',
            'scrutiny_date': datetime.now().strftime('%B %d, %Y'),
            'bill_summary': {
                'main_items_total': data.get('bill_total', 0.0),
                'main_items_premium': data.get('bill_premium', 0.0),
                'main_items_grand_total': data.get('bill_grand_total', 0.0),
                'extra_items_total': data.get('extra_items_total', 0.0),
                'extra_items_premium': data.get('extra_premium', 0.0),
                'extra_items_grand_total': data.get('extra_items_sum', 0.0),
                'final_payable_amount': data.get('total_amount', 0.0)
            }
        }
    
    def _prepare_extra_items_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for extra items statement."""
        return {
            'page_title': 'Extra Items Statement',
            'document_type': 'Additional Work Items',
            'has_extra_items': len(data.get('extra_items', [])) > 0,
            'extra_items_count': len(data.get('extra_items', []))
        }
    
    def _prepare_certificate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for certificates."""
        return {
            'page_title': 'Work Completion Certificate',
            'document_type': 'Official Certification',
            'certificate_date': datetime.now().strftime('%B %d, %Y'),
            'work_status': 'Completed as per specifications',
            'quality_status': 'Approved and accepted'
        }
    
    def generate_excel_outputs(self, data: Dict[str, Any]) -> Dict[str, bytes]:
        """
        Generate Excel outputs for each document template.
        
        Args:
            data: Processed data from ExcelProcessor
            
        Returns:
            Dictionary with document names as keys and Excel file bytes as values
        """
        excel_outputs = {}
        
        try:
            # Generate Excel for bill items
            if 'bill_items' in data and data['bill_items']:
                excel_outputs['bill_items'] = self._create_excel_from_data(
                    data['bill_items'], 
                    'Bill Items Summary'
                )
            
            # Generate Excel for extra items
            if 'extra_items' in data and data['extra_items']:
                excel_outputs['extra_items'] = self._create_excel_from_data(
                    data['extra_items'],
                    'Extra Items Summary'
                )
            
            # Generate Excel for deviation analysis
            deviation_data = self._prepare_deviation_data(data)
            if deviation_data.get('deviations'):
                excel_outputs['deviation_analysis'] = self._create_excel_from_data(
                    deviation_data['deviations'],
                    'Deviation Analysis'
                )
            
            # Generate Excel for financial summary
            financial_summary = [
                {
                    'Category': 'Main Items Total',
                    'Amount': data.get('bill_total', 0.0)
                },
                {
                    'Category': 'Main Items Premium',
                    'Amount': data.get('bill_premium', 0.0)
                },
                {
                    'Category': 'Main Items Grand Total',
                    'Amount': data.get('bill_grand_total', 0.0)
                },
                {
                    'Category': 'Extra Items Total',
                    'Amount': data.get('extra_items_total', 0.0)
                },
                {
                    'Category': 'Extra Items Premium',
                    'Amount': data.get('extra_premium', 0.0)
                },
                {
                    'Category': 'Extra Items Grand Total',
                    'Amount': data.get('extra_items_sum', 0.0)
                },
                {
                    'Category': 'Final Payable Amount',
                    'Amount': data.get('total_amount', 0.0)
                }
            ]
            
            excel_outputs['financial_summary'] = self._create_excel_from_data(
                financial_summary,
                'Financial Summary'
            )
            
            return excel_outputs
            
        except Exception as e:
            st.warning(f"⚠️ Could not generate all Excel outputs: {str(e)}")
            return {}
    
    def _create_excel_from_data(self, data_list: List[Dict], sheet_name: str) -> bytes:
        """Create Excel file from data list."""
        try:
            # Create DataFrame from data
            df = pd.DataFrame(data_list)
            
            # Create Excel writer
            from io import BytesIO
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Get workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                
                # Apply basic formatting
                from openpyxl.styles import Font, PatternFill, Alignment
                
                # Header formatting
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
                
                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center")
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            st.warning(f"⚠️ Could not create Excel file for {sheet_name}: {str(e)}")
            return b''
    
    def _get_builtin_template(self, doc_name: str) -> str:
        """Get built-in template content as fallback."""
        
        # Basic HTML template structure
        base_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ data.page_title or 'Infrastructure Document' }}</title>
            <style>
                @page { size: A4; margin: 10mm; }
                * { box-sizing: border-box; }
                body { font-family: Arial, sans-serif; font-size: 10pt; margin: 0; }
                h1 { text-align: center; margin: 0 0 8px 0; font-size: 16pt; }
                table { width: 100%; border-collapse: collapse; table-layout: fixed; }
                thead { display: table-header-group; }
                tr { break-inside: avoid; }
                th, td { border: 1px solid #000; padding: 4px; text-align: left; vertical-align: top; word-wrap: break-word; }
                th { background: #f0f0f0; text-align: center; }
                .info-section { margin-bottom: 1rem; }
                .total-row { font-weight: bold; background: #f5f5f5; }
            </style>
        </head>
        <body>
            <h1>{{ data.page_title or 'INFRASTRUCTURE DOCUMENT' }}</h1>
            
            <div class="info-section">
                <p><strong>Agreement No:</strong> {{ data.agreement_no }}</p>
                <p><strong>Name of Work:</strong> {{ data.name_of_work }}</p>
                <p><strong>Name of Firm:</strong> {{ data.name_of_firm }}</p>
                <p><strong>Date of Commencement:</strong> {{ data.date_commencement }}</p>
                <p><strong>Schedule Date of Completion:</strong> {{ data.date_completion }}</p>
                <p><strong>Actual Date of Completion:</strong> {{ data.actual_completion }}</p>
            </div>
            
            {% if data.bill_items %}
            <table>
                <thead>
                    <tr>
                        <th>Item No.</th>
                        <th>Description</th>
                        <th>Unit</th>
                        <th>Quantity</th>
                        <th>Rate</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in data.bill_items %}
                    <tr>
                        <td>{{ item.item_no or item.serial_no }}</td>
                        <td>{{ item.description }}</td>
                        <td>{{ item.unit }}</td>
                        <td>{{ "%.2f"|format(item.quantity_bill or item.quantity or 0) }}</td>
                        <td>{{ "%.2f"|format(item.rate or 0) }}</td>
                        <td>{{ "%.2f"|format(item.amount or 0) }}</td>
                    </tr>
                    {% endfor %}
                    <tr class="total-row">
                        <td colspan="5">Total Amount</td>
                        <td>{{ "%.2f"|format(data.bill_total or 0) }}</td>
                    </tr>
                </tbody>
            </table>
            {% endif %}
            
            <div style="margin-top: 2rem; text-align: center; font-size: 8pt; color: #666;">
                Generated on {{ data.generation_date }} at {{ data.generation_time }}
            </div>
        </body>
        </html>
        """
        
        return base_template
    
    def _format_currency(self, value):
        return f"₹ {value:,.2f}"
    
    def _format_date(self, date):
        return date.strftime('%B %d, %Y')
