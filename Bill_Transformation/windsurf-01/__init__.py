"""
Windsurf - Advanced Bill Generation and Processing

A comprehensive solution for generating, processing, and managing billing documents
with support for multiple output formats including HTML, PDF, and DOCX.
"""

__version__ = '0.4.0'
__author__ = 'Windsurf Team'

# Import key components for easier access
from .document_generator import DocumentGeneratorV04
from .utils.excel_processor import ExcelProcessorV01
from .batch.processor import BatchProcessor

# Initialize logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='windsurf.log'
)

logger = logging.getLogger(__name__)
logger.info(f"Windsurf v{__version__} initialized")
