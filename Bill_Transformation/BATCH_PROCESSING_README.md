# Bill Transformation - Batch Processing Module

This module provides batch processing capabilities for transforming Excel bill files into multiple document formats (HTML, PDF, DOCX) using templates. It combines the structure of V0.1 with the improved first page and deviation statement logic from V0.4.

## Features

- Process multiple Excel bill files in a single batch
- Generate documents for all 6 standard templates in order:
  1. First Page
  2. Deviation Statement
  3. Extra Items
  4. Note Sheet
  5. Certificate II
  6. Certificate III
- Support for multiple output formats (HTML, PDF, DOCX)
- Parallel processing for improved performance
- Comprehensive logging and error handling
- ZIP archive generation for easy distribution

## Prerequisites

- Python 3.7+
- wkhtmltopdf (for PDF generation)

## Installation

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Install wkhtmltopdf:
   - Windows: Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)
   - Ubuntu/Debian: `sudo apt-get install wkhtmltopdf`
   - macOS: `brew install wkhtmltopdf`

## Usage

### Command Line Interface

```bash
# Process all Excel files in the test_files directory
python test_batch_processor.py

# Process specific files
python test_batch_processor.py path/to/file1.xlsx path/to/file2.xlsx

# Process all Excel files in a directory
python test_batch_processor.py path/to/directory/
```

### Programmatic Usage

```python
from batch_processor import process_batch_files

# Process multiple files
results = process_batch_files(
    input_files=["file1.xlsx", "file2.xlsx"],
    output_dir="output",
    premium_percentage=10.0,
    reverse_font=False,
    generate_html=True,
    generate_pdf=True,
    generate_docx=True
)

# Check results
print(f"Processed {len(results.get('success', []))} files successfully")
print(f"Failed: {len(results.get('failed', []))}")
if 'zip_path' in results:
    print(f"Output ZIP: {results['zip_path']}")
```

## Output Structure

Processed files are organized in the following structure:

```
output/
├── <filename1>_<timestamp>/
│   ├── first_page.html
│   ├── first_page.pdf
│   ├── first_page.docx
│   ├── deviation_statement.html
│   ├── deviation_statement.pdf
│   └── ...
├── <filename2>_<timestamp>/
│   └── ...
└── batch_output_<timestamp>.zip
```

## Configuration

You can customize the following parameters when using the batch processor:

- `premium_percentage`: Premium percentage to apply to bills (default: 10.0)
- `reverse_font`: Use reverse font colors (default: False)
- `generate_html`: Generate HTML output (default: True)
- `generate_pdf`: Generate PDF output (default: True)
- `generate_docx`: Generate DOCX output (default: True)

## Error Handling

- Failed files are logged with detailed error messages
- Processing continues even if some files fail
- Comprehensive logs are saved to `batch_processing.log`

## Performance

- Uses parallel processing for improved performance
- Processes multiple files concurrently
- Memory-efficient handling of large Excel files

## Troubleshooting

1. **PDF Generation Fails**
   - Ensure wkhtmltopdf is installed and in your system PATH
   - Check the logs for specific error messages

2. **Missing Templates**
   - Ensure all required template files are in the `templates` directory
   - Verify template file permissions

3. **Excel File Issues**
   - Check that input files are valid Excel files (.xlsx, .xls, .xlsm)
   - Verify that required sheets and columns are present

## License

This project is licensed under the MIT License.
