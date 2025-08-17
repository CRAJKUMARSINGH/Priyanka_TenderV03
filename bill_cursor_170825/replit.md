# Overview

This is an Infrastructure Billing System designed to automate the generation of professional billing documents from Excel data. The system processes Excel files containing work order details and generates comprehensive documentation packages including HTML documents, LaTeX templates, PDFs, and certificates. It's built with Streamlit for a user-friendly web interface and focuses on creating Election Commission compliant billing documentation for infrastructure projects.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Streamlit Web Application**: Single-page application (`app.py`) providing an intuitive interface for file uploads and document generation
- **Responsive UI Design**: Custom CSS styling with green gradient headers and professional appearance
- **Real-time Processing**: Interactive feedback during file processing and document generation

## Backend Architecture
- **Modular Utility System**: Organized into specialized utility classes in the `utils/` package
- **Template-Based Generation**: Separation of presentation logic using Jinja2 templates
- **Multi-format Output**: Support for both HTML and LaTeX document generation
- **Error Handling**: Comprehensive exception handling with user-friendly error messages

## Data Processing Pipeline
- **Excel Processing**: Flexible column mapping system to handle various Excel file formats
- **Sheet Validation**: Required sheets include 'Title', 'Work Order', 'Bill Quantity' with optional 'Extra Items'
- **Data Transformation**: Conversion of Excel data into structured format for document generation
- **Template Rendering**: Dynamic content injection into predefined document templates

## Document Generation System
- **HTML Templates**: Professional HTML documents with CSS styling for web viewing
- **LaTeX Templates**: Compliance-ready LaTeX documents for PDF generation
- **PDF Conversion**: Multiple conversion paths using WeasyPrint for HTML and LaTeX compilers
- **Document Types**: Six core document types including first page, deviation statements, note sheets, extra items, and certificates

## File Management
- **ZIP Packaging**: Organized file structure with numbered folders for different document types
- **Temporary File Handling**: Safe temporary file management for processing operations
- **Download Management**: Streamlined download process for complete document packages

# External Dependencies

## Core Framework
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Excel file processing and data manipulation
- **Jinja2**: Template engine for dynamic document generation

## Document Processing
- **openpyxl**: Excel file reading and writing capabilities
- **WeasyPrint**: HTML to PDF conversion (optional dependency)
- **LaTeX Distribution**: External LaTeX compiler (pdflatex/xelatex) for LaTeX to PDF conversion

## File Operations
- **zipfile**: Built-in Python library for ZIP package creation
- **tempfile**: Temporary file management for processing operations
- **datetime**: Timestamp generation for document metadata

## Template System
- **HTML Templates**: Located in `templates/html/` directory with professional styling
- **LaTeX Templates**: Located in `templates/latex/` directory for compliance documentation
- **CSS Styling**: Embedded styles for professional document appearance

The system is designed to be self-contained with graceful degradation when optional dependencies are unavailable, ensuring core functionality remains accessible even in limited environments.