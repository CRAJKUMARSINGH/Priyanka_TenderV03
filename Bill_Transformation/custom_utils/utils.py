import os
import subprocess
import platform
import logging
import shutil

def setup_wkhtmltopdf():
    """Setup wkhtmltopdf for PDF generation"""
    logger = logging.getLogger(__name__)
    
    try:
        # Try to find wkhtmltopdf
        result = subprocess.run(['wkhtmltopdf', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("wkhtmltopdf found and working")
            return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try alternative paths
    possible_paths = [
        '/usr/bin/wkhtmltopdf',
        '/usr/local/bin/wkhtmltopdf',
        'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
        'C:\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info(f"wkhtmltopdf found at: {path}")
                    return True
            except:
                continue
    
    logger.warning("wkhtmltopdf not found - PDF generation will be limited")
    return False

def resolve_logo_url(logo_path):
    """Resolve logo URL for templates"""
    if not logo_path:
        return ""
    
    # If it's already a URL, return as is
    if logo_path.startswith('http'):
        return logo_path
    
    # If it's a local file, check if exists
    if os.path.exists(logo_path):
        return f"file://{os.path.abspath(logo_path)}"
    
    # Default to empty if not found
    return ""

def validate_template_data(data):
    """Validate template data structure"""
    required_fields = ['project_name', 'contractor_name', 'bill_number', 'bill_date']
    
    for field in required_fields:
        if field not in data or not data[field]:
            data[field] = f"{field.replace('_', ' ').title()} Not Available"
    
    return data

def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"₹ {float(amount):,.2f}"
    except:
        return "₹ 0.00"

def format_number(number):
    """Format number with proper comma separation"""
    try:
        return f"{float(number):,.2f}"
    except:
        return "0.00"

def safe_get(data, key, default="N/A"):
    """Safely get value from dictionary"""
    return data.get(key, default) if data else default
