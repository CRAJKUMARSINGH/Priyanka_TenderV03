import pandas as pd
import numpy as np

def debug_excel_structure():
    """Debug the structure of the Excel file to understand why works aren't being detected."""
    try:
        # Read the Excel file
        file_path = 'attached_assets/NIT_10 works_1753153056016.xlsx'
        
        # Try reading different sheets
        xl_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Read the first sheet
        df = pd.read_excel(file_path, sheet_name=0)
        print(f"\nDataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Print first 20 rows to see structure
        print("\nFirst 20 rows:")
        for i, row in df.head(20).iterrows():
            print(f"Row {i}: {list(row)}")
        
        # Look for patterns that indicate work data
        print("\n=== Looking for Work Headers ===")
        for idx, row in df.iterrows():
            row_str = ' '.join(str(cell).upper() for cell in row if pd.notna(cell))
            if any(keyword in row_str for keyword in ['ITEM NO', 'NAME OF WORK', 'ESTIMATED COST', 'WORK NO']):
                print(f"Row {idx} (potential header): {row_str}")
        
        # Look for numeric patterns that might be work items
        print("\n=== Looking for Numeric Patterns ===")
        for idx, row in df.iterrows():
            first_cell = str(row.iloc[0]).strip()
            if first_cell and first_cell.replace('.', '').isdigit():
                print(f"Row {idx} (numeric start): {list(row)}")
        
    except Exception as e:
        print(f"Error debugging Excel file: {e}")

if __name__ == "__main__":
    debug_excel_structure()
