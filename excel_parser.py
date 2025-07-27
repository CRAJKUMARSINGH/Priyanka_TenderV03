import pandas as pd
import logging
from typing import Dict, Any, Optional
import re
from date_utils import DateUtils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExcelParser:
    """Enhanced Excel parser with robust date handling for NIT documents."""
    
    def __init__(self):
        self.date_utils = DateUtils()
    
    def parse_nit_excel(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse NIT Excel file and extract work information with enhanced date handling.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Dictionary containing parsed work information or None if parsing fails
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
            
            # Try to find the main sheet with tender information
            main_sheet = self._find_main_sheet(df)
            if main_sheet is None:
                logging.error("Could not find main sheet with tender information")
                return None
            
            # Extract work information
            work_data = self._extract_work_info(main_sheet)
            
            if work_data:
                logging.info(f"Successfully parsed NIT: {work_data['nit_number']}")
                return work_data
            else:
                logging.error("Failed to extract work information from Excel")
                return None
                
        except Exception as e:
            logging.error(f"Error parsing Excel file: {e}")
            return None
    
    def _find_main_sheet(self, sheets_dict: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
        """
        Find the main sheet containing tender information.
        
        Args:
            sheets_dict: Dictionary of sheet names and DataFrames
            
        Returns:
            Main DataFrame or None if not found
        """
        # Priority order for sheet selection
        priority_keywords = [
            'tender', 'nit', 'notice', 'main', 'sheet1', 'work'
        ]
        
        # First, try to find by keywords
        for keyword in priority_keywords:
            for sheet_name, df in sheets_dict.items():
                if keyword.lower() in sheet_name.lower():
                    return df
        
        # If no keyword match, return the first non-empty sheet
        for sheet_name, df in sheets_dict.items():
            if not df.empty:
                return df
        
        return None
    
    def _extract_work_info(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Extract work information from the main DataFrame with support for multiple works.
        
        Args:
            df: Main DataFrame containing tender information
            
        Returns:
            Dictionary with extracted work information including multiple works
        """
        try:
            # Convert DataFrame to string for easier searching
            df_str = df.astype(str).fillna('')
            
            # Extract NIT number from header area
            nit_number = self._extract_nit_number(df_str)
            if not nit_number:
                nit_number = f"NIT-{self.date_utils.get_current_date().replace('/', '')}-001"
            
            # Extract dates from header area
            nit_date = self._extract_nit_date(df_str)
            receipt_date = self._extract_receipt_date(df_str)
            opening_date = self._extract_opening_date(df_str)
            
            # Extract all works from the NIT
            works = self._extract_multiple_works(df)
            
            if not works:
                logging.error("No works found in NIT")
                return None
            
            # Create a combined work name if multiple works
            if len(works) > 1:
                work_name = f"Multiple Works Package (Total: {len(works)} works)"
            else:
                work_name = works[0]['name']
            
            # Calculate total estimated cost
            total_estimated_cost = sum(work.get('estimated_cost', 0) for work in works)
            total_earnest_money = sum(work.get('earnest_money', 0) for work in works)
            
            return {
                'work_name': work_name,
                'nit_number': nit_number,
                'nit_date': nit_date,
                'receipt_date': receipt_date,
                'opening_date': opening_date,
                'estimated_cost': total_estimated_cost,
                'earnest_money': total_earnest_money,
                'total_works': len(works),
                'works': works,
                'time_completion': max((work.get('time_completion', 6) for work in works), default=6)
            }
            
        except Exception as e:
            logging.error(f"Error extracting work info: {e}")
            return None
    
    def _extract_multiple_works(self, df: pd.DataFrame) -> list:
        """Extract all individual works from the NIT DataFrame."""
        works = []
        
        try:
            # Look for work data starting from row with headers
            work_start_row = None
            header_row = None
            
            # Find the header row containing work information columns
            for idx, row in df.iterrows():
                row_str = ' '.join(str(cell).upper() for cell in row if pd.notna(cell))
                if ('ITEM NO' in row_str and 'NAME OF WORK' in row_str and 
                    ('ESTIMATED COST' in row_str or 'ESTIMATED' in row_str)):
                    header_row = idx
                    work_start_row = idx + 1
                    logging.info(f"Found work header at row {idx}: {row_str}")
                    break
            
            if header_row is None or work_start_row is None:
                logging.warning("Could not find work data headers")
                return []
            
            # Extract works from subsequent rows
            for idx in range(work_start_row, len(df)):
                row = df.iloc[idx]
                
                # Skip empty rows
                if row.isna().all():
                    continue
                
                # Try to extract work information
                work_data = self._parse_work_row(row, df.columns)
                if work_data:
                    works.append(work_data)
                    
            logging.info(f"Found {len(works)} works in NIT")
            return works
            
        except Exception as e:
            logging.error(f"Error extracting multiple works: {e}")
            return []
    
    def _parse_work_row(self, row, columns) -> Optional[Dict[str, Any]]:
        """Parse a single work row from the DataFrame."""
        try:
            work_data = {}
            
            # Convert row to list for easier access, handle mixed types
            row_values = []
            for val in row:
                if pd.notna(val):
                    if isinstance(val, str):
                        row_values.append(val.strip())
                    else:
                        row_values.append(val)
                else:
                    row_values.append('')
            
            # Skip if first cell is empty or not a number (likely not a work row)
            first_val = str(row_values[0]).strip()
            if not first_val or first_val == '' or first_val == 'nan':
                return None
                
            # Try to convert first value to number
            try:
                item_no = int(float(first_val))
                work_data['item_no'] = item_no
            except (ValueError, TypeError):
                return None
            
            # Extract work name (second column)
            work_data['name'] = str(row_values[1]).strip() if len(row_values) > 1 else f"Work {work_data['item_no']}"
            
            # Extract estimated cost (third column, convert from lacs to rupees)
            try:
                if len(row_values) > 2 and row_values[2] and str(row_values[2]) != 'nan':
                    estimated_cost_lacs = float(row_values[2])
                    work_data['estimated_cost'] = int(estimated_cost_lacs * 100000)  # Convert lacs to rupees
                else:
                    work_data['estimated_cost'] = 0
            except (ValueError, TypeError):
                work_data['estimated_cost'] = 0
            
            # Extract G-Schedule amount (fourth column)
            try:
                if len(row_values) > 3 and row_values[3]:
                    work_data['g_schedule_amount'] = int(float(row_values[3]))
                else:
                    work_data['g_schedule_amount'] = work_data['estimated_cost']
            except (ValueError, TypeError):
                work_data['g_schedule_amount'] = work_data['estimated_cost']
            
            # Extract time of completion (fifth column)
            try:
                if len(row_values) > 4 and row_values[4]:
                    work_data['time_completion'] = int(float(row_values[4]))
                else:
                    work_data['time_completion'] = 6
            except (ValueError, TypeError):
                work_data['time_completion'] = 6
            
            # Extract earnest money (sixth column)
            try:
                if len(row_values) > 5 and row_values[5]:
                    work_data['earnest_money'] = int(float(row_values[5]))
                else:
                    work_data['earnest_money'] = int(work_data['estimated_cost'] * 0.02)  # 2% of estimated cost
            except (ValueError, TypeError):
                work_data['earnest_money'] = int(work_data['estimated_cost'] * 0.02)
            
            return work_data
            
        except Exception as e:
            logging.error(f"Error parsing work row: {e}")
            return None
    
    def _extract_nit_date(self, df_str: pd.DataFrame) -> str:
        """Extract NIT calling date from DataFrame."""
        return self._extract_date_by_keyword(df_str, ['calling', 'nit', 'date of calling'])
    
    def _extract_receipt_date(self, df_str: pd.DataFrame) -> str:
        """Extract receipt date from DataFrame."""
        return self._extract_date_by_keyword(df_str, ['receipt', 'date of receipt'])
    
    def _extract_opening_date(self, df_str: pd.DataFrame) -> str:
        """Extract opening date from DataFrame."""
        return self._extract_date_by_keyword(df_str, ['opening', 'date of opening'])
    
    def _extract_date_by_keyword(self, df_str: pd.DataFrame, keywords: list) -> str:
        """Extract date based on keywords from DataFrame."""
        try:
            for _, row in df_str.iterrows():
                for col in df_str.columns:
                    cell_value = str(row[col]).lower()
                    
                    # Check if cell contains any of the keywords
                    if any(keyword in cell_value for keyword in keywords):
                        # Look for date in the same row, next columns
                        for next_col in df_str.columns[df_str.columns.get_loc(col):]:
                            next_cell = str(row[next_col])
                            date_result = self.date_utils.parse_date(next_cell)
                            if date_result:
                                return date_result
                        
                        # Look for date in next row, same column pattern
                        try:
                            next_row_idx = df_str.index[df_str.index.get_loc(row.name) + 1]
                            next_row = df_str.loc[next_row_idx]
                            next_cell = str(next_row[col])
                            date_result = self.date_utils.parse_date(next_cell)
                            if date_result:
                                return date_result
                        except (IndexError, KeyError):
                            pass
            
            return self.date_utils.get_current_date()
            
        except Exception as e:
            logging.error(f"Error extracting date by keyword: {e}")
            return self.date_utils.get_current_date()
    
    def _extract_work_name(self, df_str: pd.DataFrame) -> Optional[str]:
        """Extract work name from DataFrame."""
        work_keywords = [
            'work', 'name of work', 'work name', 'project', 'tender for'
        ]
        
        for _, row in df_str.iterrows():
            for col in df_str.columns:
                cell_value = str(row[col]).lower()
                
                for keyword in work_keywords:
                    if keyword in cell_value and len(cell_value) > 20:
                        # Clean and return work name
                        work_name = str(row[col]).strip()
                        if len(work_name) > 10:  # Ensure it's not just the header
                            return work_name
        
        # Fallback: look for long text that might be work name
        for _, row in df_str.iterrows():
            for col in df_str.columns:
                cell_value = str(row[col]).strip()
                if 50 <= len(cell_value) <= 500 and 'work' in cell_value.lower():
                    return cell_value
        
        return "Extracted Work Name"
    
    def _extract_nit_number(self, df_str: pd.DataFrame) -> Optional[str]:
        """Extract NIT number from DataFrame."""
        nit_patterns = [
            r'NIT\s*[:\-]?\s*([A-Z0-9\-\/]+)',
            r'TENDER\s*NO\s*[:\-]?\s*([A-Z0-9\-\/]+)',
            r'NOTICE\s*NO\s*[:\-]?\s*([A-Z0-9\-\/]+)',
            r'([A-Z0-9]+\/[A-Z0-9]+\/\d{4})',
            r'([A-Z0-9]+\-[A-Z0-9]+\-\d{4})'
        ]
        
        for _, row in df_str.iterrows():
            for col in df_str.columns:
                cell_value = str(row[col]).upper()
                
                for pattern in nit_patterns:
                    match = re.search(pattern, cell_value)
                    if match:
                        return match.group(1) if match.lastindex else match.group(0)
        
        # Generate default NIT number if not found
        from datetime import datetime
        return f"NIT-{datetime.now().strftime('%Y%m%d')}-001"
    
    def _extract_estimated_cost(self, df_str: pd.DataFrame) -> Optional[float]:
        """Extract estimated cost from DataFrame."""
        cost_keywords = [
            'estimated cost', 'estimate', 'cost', 'amount', 'value', 'budget'
        ]
        
        for _, row in df_str.iterrows():
            for col in df_str.columns:
                cell_value = str(row[col]).lower()
                
                # Check if this cell contains cost keywords
                if any(keyword in cell_value for keyword in cost_keywords):
                    # Look for numeric values in nearby cells
                    for search_col in df_str.columns:
                        search_value = str(row[search_col])
                        cost = self._extract_numeric_value(search_value)
                        if cost and cost > 1000:  # Reasonable minimum cost
                            return cost
        
        # Fallback: search for large numeric values
        for _, row in df_str.iterrows():
            for col in df_str.columns:
                cell_value = str(row[col])
                cost = self._extract_numeric_value(cell_value)
                if cost and 10000 <= cost <= 100000000:  # Reasonable range
                    return cost
        
        return None
    
    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text string."""
        try:
            # Remove common currency symbols and formatting
            clean_text = re.sub(r'[₹$,\s]', '', text)
            
            # Try to extract number
            number_match = re.search(r'(\d+\.?\d*)', clean_text)
            if number_match:
                return float(number_match.group(1))
        except:
            pass
        
        return None
    
    def _extract_date(self, df_str: pd.DataFrame) -> Optional[str]:
        """Extract date from DataFrame with enhanced date handling."""
        date_keywords = [
            'date', 'dated', 'on', 'issued', 'published', 'tender date'
        ]
        
        # Look for date keywords first
        for _, row in df_str.iterrows():
            for col in df_str.columns:
                cell_value = str(row[col]).lower()
                
                if any(keyword in cell_value for keyword in date_keywords):
                    # Search nearby cells for date values
                    for search_col in df_str.columns:
                        search_value = str(row[search_col]).strip()
                        parsed_date = self.date_utils.parse_date(search_value)
                        if parsed_date:
                            return self.date_utils.format_date(parsed_date)
        
        # Fallback: search all cells for date patterns
        for _, row in df_str.iterrows():
            for col in df_str.columns:
                cell_value = str(row[col]).strip()
                parsed_date = self.date_utils.parse_date(cell_value)
                if parsed_date:
                    return self.date_utils.format_date(parsed_date)
        
        # Default to current date if no date found
        return self.date_utils.get_current_date()
    
    def _extract_earnest_money(self, df_str: pd.DataFrame, estimated_cost: float) -> float:
        """Extract earnest money or calculate default."""
        em_keywords = [
            'earnest money', 'earnest', 'em', 'security deposit', 'deposit'
        ]
        
        for _, row in df_str.iterrows():
            for col in df_str.columns:
                cell_value = str(row[col]).lower()
                
                if any(keyword in cell_value for keyword in em_keywords):
                    # Look for numeric values in nearby cells
                    for search_col in df_str.columns:
                        search_value = str(row[search_col])
                        amount = self._extract_numeric_value(search_value)
                        if amount and 100 <= amount <= estimated_cost * 0.1:  # Reasonable range
                            return amount
        
        # Default to 2% of estimated cost
        return round(estimated_cost * 0.02, 2)
    
    def _extract_time_completion(self, df_str: pd.DataFrame) -> str:
        """Extract time of completion."""
        time_keywords = [
            'completion', 'duration', 'time', 'period', 'months', 'days'
        ]
        
        for _, row in df_str.iterrows():
            for col in df_str.columns:
                cell_value = str(row[col]).lower()
                
                if any(keyword in cell_value for keyword in time_keywords):
                    # Look for time patterns
                    time_patterns = [
                        r'(\d+)\s*months?',
                        r'(\d+)\s*days?',
                        r'(\d+)\s*weeks?'
                    ]
                    
                    for pattern in time_patterns:
                        match = re.search(pattern, cell_value)
                        if match:
                            number = match.group(1)
                            if 'month' in cell_value:
                                return f"{number} Months"
                            elif 'day' in cell_value:
                                return f"{number} Days"
                            elif 'week' in cell_value:
                                return f"{number} Weeks"
        
        # Default to 3 months
        return "3 Months"
