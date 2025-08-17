# Contractor Bill Template System

A React-based application for generating accurate contractor bills using professional HTML templates. This system processes bill data and renders it using the provided templates for different sections of contractor bills.

## Features

- **Multiple Template Support**: Supports 5 different template types:
  - First Page - Main contractor bill with items and totals
  - Certificate II - Signatures and certifications
  - Certificate III - Memorandum of payments
  - Deviation Statement - Work order vs executed quantities
  - Extra Items - Additional work items

- **Data Processing**: Handles complex bill calculations including:
  - Main bill items with quantities, rates, and amounts
  - Extra items and premium calculations
  - Deviation analysis between work order and executed quantities
  - Tax deductions (SD, IT, GST, LC)
  - Net payable calculations

- **PDF Generation**: Print-ready output with proper formatting for A4 paper

- **Sample Data**: Includes comprehensive sample data for testing and demonstration

## Template Structure

The application uses the following HTML templates located in `src/templates/`:

1. `first_page.html` - Main bill page with all items and totals
2. `certificate_ii.html` - Certificate and signatures page
3. `certificate_iii.html` - Memorandum of payments
4. `deviation_statement.html` - Deviation analysis table
5. `extra_items.html` - Extra items listing

## Data Format

The application expects JSON data in the following structure:

```typescript
interface BillData {
  // Header information
  agreement_no: string;
  name_of_work: string;
  name_of_firm: string;
  date_commencement: string;
  date_completion: string;
  actual_completion: string;
  
  // Bill items and calculations
  bill_items: BillItem[];
  extra_items: ExtraItem[];
  deviation_items: DeviationItem[];
  
  // Financial totals
  totals: BillTotals;
  deviation_summary: DeviationSummary;
  
  // Certificate information
  measurement_officer: string;
  officer_name: string;
  // ... other fields
}
```

## Usage

1. **Load Sample Data**: Click "Load Sample Data" to see the system in action
2. **Upload JSON**: Upload your own bill data in JSON format
3. **Select Template**: Choose which template to view/print
4. **Print/Download**: Generate PDF output for printing

## Key Features

- **Accurate Calculations**: Handles complex financial calculations with proper rounding
- **Date Formatting**: Automatically converts dates from YYYY-MM-DD to DD/MM/YYYY format
- **Responsive Design**: Works on desktop and mobile devices
- **Print Optimization**: Formatted for A4 paper with proper page breaks

## Technical Implementation

- Built with React and TypeScript
- Uses Tailwind CSS for styling
- Template rendering system converts data to HTML
- Print functionality opens formatted content in new window
- Modular architecture with separate components for each template type

## Getting Started

1. Install dependencies: `npm install`
2. Start development server: `npm run dev`
3. Load sample data or upload your own JSON file
4. Select templates to view different sections
5. Use print function to generate PDF output

The system is designed to be production-ready and can handle real contractor bill data with accurate calculations and professional formatting.
</parameter>