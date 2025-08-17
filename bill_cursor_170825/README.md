<<<<<<< HEAD
# bill_cursor_170825
=======
# 🏗️ Bill Generator

A Streamlit-based application for generating billing documents from Excel data using customizable HTML and LaTeX templates.

## Features

- Upload Excel files with billing data
- Generate documents using HTML or LaTeX templates
- Download individual files or as a ZIP archive
- Responsive and user-friendly interface
- Support for multiple document types (first page, deviation statement, etc.)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- For LaTeX support: A working LaTeX distribution (e.g., MiKTeX, TeX Live)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bill-generator
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up templates:
   - Place your HTML templates in `templates/html/`
   - Place your LaTeX templates in `templates/latex/`

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. In the application:
   - Select the template type (HTML or LaTeX)
   - Upload your Excel file
   - Click "Generate Documents"
   - Download the generated files individually or as a ZIP archive

## Template Format

Templates should be placed in their respective directories and named as follows:

- `first_page.{html|tex}`
- `deviation_statement.{html|tex}`
- `extra_items.{html|tex}`
- `note_sheet.{html|tex}`
- `certificate_ii.{html|tex}`
- `certificate_iii.{html|tex}`

Use Jinja2 templating syntax to insert data from your Excel file. For example:

```html
<h1>Invoice for {{ customer_name }}</h1>
<p>Amount: ${{ amount }}</p>
```

## Directory Structure

```
bill-generator/
├── templates/
│   ├── html/
│   │   ├── first_page.html
│   │   ├── deviation_statement.html
│   │   └── ...
│   └── latex/
│       ├── first_page.tex
│       ├── deviation_statement.tex
│       └── ...
├── output/
│   └── (generated files)
├── app.py
├── requirements.txt
└── README.md
```

## Notes

- The application processes the first row of your Excel file for template rendering
- Ensure your Excel column names match the variable names used in your templates
- For LaTeX support, make sure a LaTeX distribution is installed and in your system PATH

## License

This project is licensed under the MIT License - see the LICENSE file for details.
>>>>>>> d6d9290 (Fix LaTeX compilation error by replacing abs filter with direct negation)
