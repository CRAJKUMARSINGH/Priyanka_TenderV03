import pandas as pd
import streamlit as st
from typing import Dict, List, Any, Optional
import traceback

class ExcelProcessor:
    """
    Utility class for processing Excel files and extracting billing data.
    Handles multiple sheets with flexible column name mapping and robust error handling.
    """
    
    def __init__(self):
        self.required_sheets = ['Title', 'Work Order', 'Bill Quantity']
        self.optional_sheets = ['Extra Items']
        
        # Column name variations for flexible mapping
        self.column_mappings = {
            'item_no': ['Item No', 'Item', 'S.No', 'Sr.No', 'Serial No'],
            'description': ['Description', 'Description of Work', 'Item Description', 'Work Description'],
            'unit': ['Unit', 'Units', 'UOM'],
            'quantity': ['Quantity', 'Qty', 'Work Order Qty', 'Ordered Qty'],
            'quantity_bill': ['Bill Qty', 'Bill Quantity', 'Executed Qty', 'Completed Qty'],
            'rate': ['Rate', 'Unit Rate', 'Rate per Unit'],
            'amount': ['Amount', 'Total Amount', 'Total'],
            'remark': ['Remark', 'Remarks', 'Comments', 'Notes']
        }
    
    def process_file(self, uploaded_file) -> Optional[Dict[str, Any]]:
        """
        Process the uploaded Excel file and extract all necessary data.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Dictionary containing processed data or None if processing fails
        """
        try:
            # Read Excel file with all sheets
            excel_data = pd.read_excel(uploaded_file, sheet_name=None, engine='openpyxl')
            
            # Validate required sheets
            missing_sheets = [sheet for sheet in self.required_sheets if sheet not in excel_data.keys()]
            if missing_sheets:
                st.error(f"❌ Missing required sheets: {', '.join(missing_sheets)}")
                return None
            
            # Process each sheet
            processed_data = {}
            
            # Process Title sheet for project information
            title_data = self._process_title_sheet(excel_data['Title'])
            if title_data:
                processed_data.update(title_data)
            
            # Process Work Order sheet
            work_order_data = self._process_work_order_sheet(excel_data['Work Order'])
            if work_order_data:
                processed_data['work_order_items'] = work_order_data
            
            # Process Bill Quantity sheet
            bill_data = self._process_bill_quantity_sheet(excel_data['Bill Quantity'])
            if bill_data:
                processed_data['bill_items'] = bill_data
            
            # Process Extra Items sheet (optional)
            if 'Extra Items' in excel_data:
                extra_data = self._process_extra_items_sheet(excel_data['Extra Items'])
                if extra_data:
                    processed_data['extra_items'] = extra_data
            
            # Calculate totals and derived values
            self._calculate_totals(processed_data)
            
            return processed_data
            
        except Exception as e:
            st.error(f"❌ Error processing Excel file: {str(e)}")
            st.error("🔍 Please check your file format and ensure all required sheets are present.")
            return None
    
    def _process_title_sheet(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Process the Title sheet to extract project information."""
        try:
            project_info = {}
            
            # Convert DataFrame to list of lists for header processing
            header_rows = []
            for index, row in df.iterrows():
                row_data = [str(cell).strip() if pd.notna(cell) else '' for cell in row.values]
                if any(cell for cell in row_data):  # Skip empty rows
                    header_rows.append(row_data)
            
            # Extract key project information
            project_info['header'] = header_rows
            
            # Try to extract specific fields if available
            for row in header_rows:
                row_text = ' '.join(row).lower()
                if 'agreement' in row_text or 'contract' in row_text:
                    project_info['agreement_no'] = ' '.join(row)
                elif 'name of work' in row_text or 'project' in row_text:
                    project_info['name_of_work'] = ' '.join(row)
                elif 'firm' in row_text or 'contractor' in row_text:
                    project_info['name_of_firm'] = ' '.join(row)
                elif 'commencement' in row_text:
                    project_info['date_commencement'] = ' '.join(row)
                elif 'completion' in row_text and 'schedule' in row_text:
                    project_info['date_completion'] = ' '.join(row)
                elif 'actual' in row_text and 'completion' in row_text:
                    project_info['actual_completion'] = ' '.join(row)
            
            # Extract project name for smart filename generation
            if 'name_of_work' in project_info:
                # Extract a clean project name
                work_name = project_info['name_of_work']
                # Clean and format for filename
                project_name = ''.join(c for c in work_name if c.isalnum() or c in (' ', '_')).replace(' ', '_')
                project_info['project_name'] = project_name[:50]  # Limit length
            else:
                project_info['project_name'] = 'Infrastructure_Project'
            
            return project_info
            
        except Exception as e:
            st.warning(f"⚠️ Could not process Title sheet completely: {str(e)}")
            return {'project_name': 'Infrastructure_Project'}
    
    def _process_work_order_sheet(self, df: pd.DataFrame) -> Optional[List[Dict[str, Any]]]:
        """Process the Work Order sheet to extract planned work items."""
        try:
            return self._process_standard_sheet(df, 'Work Order')
        except Exception as e:
            st.warning(f"⚠️ Could not process Work Order sheet: {str(e)}")
            return []
    
    def _process_bill_quantity_sheet(self, df: pd.DataFrame) -> Optional[List[Dict[str, Any]]]:
        """Process the Bill Quantity sheet to extract actual work completed."""
        try:
            return self._process_standard_sheet(df, 'Bill Quantity')
        except Exception as e:
            st.warning(f"⚠️ Could not process Bill Quantity sheet: {str(e)}")
            return []
    
    def _process_extra_items_sheet(self, df: pd.DataFrame) -> Optional[List[Dict[str, Any]]]:
        """Process the Extra Items sheet to extract additional work."""
        try:
            return self._process_standard_sheet(df, 'Extra Items')
        except Exception as e:
            st.warning(f"⚠️ Could not process Extra Items sheet: {str(e)}")
            return []
    
    def _process_standard_sheet(self, df: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """Generic method to process standard data sheets with flexible column mapping."""
        
        # Clean the DataFrame
        df = df.dropna(how='all')  # Remove completely empty rows
        
        if df.empty:
            return []
        
        # Get column headers and create mapping
        headers = [str(col).strip() for col in df.columns]
        column_map = self._create_column_mapping(headers)
        
        items = []
        
        for index, row in df.iterrows():
            # Skip rows that appear to be headers or empty
            if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                continue
            
            item = {}
            
            # Map columns to standardized names
            for std_name, possible_names in self.column_mappings.items():
                value = None
                for possible_name in possible_names:
                    if possible_name in column_map:
                        col_index = column_map[possible_name]
                        if col_index < len(row):
                            value = row.iloc[col_index]
                            break
                
                # Process the value based on type
                if std_name in ['quantity', 'quantity_bill', 'rate', 'amount']:
                    item[std_name] = self._safe_numeric_conversion(value)
                else:
                    item[std_name] = str(value).strip() if pd.notna(value) else ''
            
            # Only add item if it has meaningful data
            if item.get('description') or item.get('item_no'):
                items.append(item)
        
        return items
    
    def _create_column_mapping(self, headers: List[str]) -> Dict[str, int]:
        """Create mapping between possible column names and their indices."""
        column_map = {}
        
        for i, header in enumerate(headers):
            # Try exact match first
            for std_name, possible_names in self.column_mappings.items():
                if header in possible_names:
                    column_map[header] = i
                    break
            else:
                # Try partial match
                header_lower = header.lower()
                for std_name, possible_names in self.column_mappings.items():
                    for possible_name in possible_names:
                        if possible_name.lower() in header_lower or header_lower in possible_name.lower():
                            column_map[header] = i
                            break
        
        return column_map
    
    def _safe_numeric_conversion(self, value) -> float:
        """Safely convert value to numeric, handling various formats and errors."""
        if pd.isna(value):
            return 0.0
        
        try:
            # Handle string values
            if isinstance(value, str):
                # Remove common non-numeric text
                cleaned = value.strip().lower()
                if cleaned in ['', 'nil', 'na', 'n/a', '-', 'above', 'below']:
                    return 0.0
                
                # Remove currency symbols and commas
                cleaned = cleaned.replace('₹', '').replace(',', '').replace('rs', '').replace('.', '')
                cleaned = ''.join(c for c in cleaned if c.isdigit() or c in '.-')
                
                if cleaned:
                    return float(cleaned)
                else:
                    return 0.0
            
            # Handle numeric values
            return float(value)
            
        except (ValueError, TypeError):
            return 0.0
    
    def _calculate_totals(self, data: Dict[str, Any]):
        """Calculate various totals and derived values."""
        try:
            # Calculate bill items total
            bill_total = 0.0
            if 'bill_items' in data:
                for item in data['bill_items']:
                    if 'amount' in item:
                        bill_total += item['amount']
                    elif 'quantity_bill' in item and 'rate' in item:
                        amount = item['quantity_bill'] * item['rate']
                        item['amount'] = amount
                        bill_total += amount
            
            data['bill_total'] = bill_total
            
            # Calculate extra items total
            extra_total = 0.0
            if 'extra_items' in data:
                for item in data['extra_items']:
                    if 'amount' in item:
                        extra_total += item['amount']
                    elif 'quantity' in item and 'rate' in item:
                        amount = item['quantity'] * item['rate']
                        item['amount'] = amount
                        extra_total += amount
            
            data['extra_items_total'] = extra_total
            
            # Calculate tender premium (assuming 10% if not specified)
            tender_premium_percent = 0.10  # 10%
            data['tender_premium_percent'] = tender_premium_percent
            
            bill_premium = bill_total * tender_premium_percent
            extra_premium = extra_total * tender_premium_percent
            
            data['bill_premium'] = bill_premium
            data['extra_premium'] = extra_premium
            
            # Calculate grand totals
            data['bill_grand_total'] = bill_total + bill_premium
            data['extra_items_sum'] = extra_total + extra_premium
            data['total_amount'] = data['bill_grand_total'] + data['extra_items_sum']
            
        except Exception as e:
            st.warning(f"⚠️ Could not calculate all totals: {str(e)}")
            # Set safe defaults
            data.setdefault('bill_total', 0.0)
            data.setdefault('extra_items_total', 0.0)
            data.setdefault('tender_premium_percent', 0.10)
            data.setdefault('bill_premium', 0.0)
            data.setdefault('extra_premium', 0.0)
            data.setdefault('bill_grand_total', 0.0)
            data.setdefault('extra_items_sum', 0.0)
            data.setdefault('total_amount', 0.0)
