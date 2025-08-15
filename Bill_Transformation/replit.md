# Overview

This is a professional contractor billing and document generation system built with Streamlit. The application processes Excel-based contractor bills (V01 format) and generates comprehensive documentation packages in multiple formats including HTML, PDF, DOCX, and LaTeX. The system transforms raw billing data into professional documents such as bills, certificates, deviation statements, and extra items reports.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application with a single-page interface
- **Layout**: Wide layout with sidebar configuration panel and main content area
- **User Interface**: Form-based upload system with real-time configuration options
- **Document Preview**: Integrated display of generated documents within the web interface

## Backend Architecture
- **Processing Pipeline**: Three-stage architecture with clear separation of concerns:
  1. **Excel Processing Layer** (`ExcelProcessorV01`): Handles Excel file parsing and data extraction
  2. **Document Generation Layer** (`DocumentGeneratorV04`): Converts processed data into multiple document formats
  3. **Utility Layer** (`custom_utils`): Provides system configuration and helper functions

## Data Processing Strategy
- **Input Format**: Excel workbooks with multiple sheets containing billing data
- **Data Structure**: Structured extraction into dictionaries containing project details, line items, deviations, and summary information
- **Validation**: Post-processing validation and data cleaning pipeline

## Document Generation System
- **Template Engine**: Jinja2 templating system with dedicated HTML templates for each document type
- **Multi-format Output**: Single data source generates HTML, PDF, DOCX, and LaTeX versions
- **PDF Generation**: wkhtmltopdf integration with fallback handling for different system configurations
- **Document Types**: 
  - Main bill template
  - First and last page summaries
  - Certificate II (Quality Compliance)
  - Certificate III (Final Approval)
  - Deviation statements
  - Extra items reports
  - Note sheets

## Template Architecture
- **Design Pattern**: Responsive HTML templates with conditional styling
- **Theme Support**: Light/dark mode support through reverse font configuration
- **Styling**: CSS Grid and Flexbox layouts with professional color schemes
- **Modularity**: Separate templates for each document type allowing independent customization

## File Management
- **Temporary Storage**: Uses system temporary directories for processing and output
- **Batch Processing**: Generates multiple document formats simultaneously
- **Archive Creation**: Packages all generated documents into downloadable ZIP archives

# External Dependencies

## Core Framework
- **Streamlit**: Web application framework for the user interface

## Data Processing
- **pandas**: DataFrame operations and data manipulation
- **openpyxl**: Excel file reading and processing
- **numpy**: Numerical computations and data handling

## Document Generation
- **Jinja2**: HTML template rendering engine
- **pdfkit**: PDF generation from HTML templates
- **python-docx**: Microsoft Word document creation
- **wkhtmltopdf**: System-level PDF rendering engine (external binary)

## System Integration
- **Platform-specific PDF tools**: Different wkhtmltopdf installations across Windows, Linux, and macOS
- **Subprocess management**: System command execution for PDF generation
- **File system operations**: Temporary file handling and archive creation

## Development Tools
- **logging**: Application logging and error tracking
- **tempfile**: Secure temporary file and directory management
- **zipfile**: Archive creation for document packages
- **io**: Buffer management for file processing