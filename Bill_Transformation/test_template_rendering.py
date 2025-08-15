import os
import sys
import logging
from datetime import datetime
from document_generator_v04 import DocumentGeneratorV04

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('template_test.log')
    ]
)
logger = logging.getLogger(__name__)

def create_test_data():
    """Create sample test data for template rendering"""
    try:
        test_data = {
            'header': [
                ['Name of Contractor or supplier:', 'ABC Construction Ltd.'],
                ['Name of Work:', 'Construction of Bridge'],
                ['Serial No. of this bill:', '12345'],
                ['No. and date of the last bill:', '12344 (01/01/2023)'],
                ['Reference to work order or Agreement:', 'WO-2023-001'],
                ['Agreement No:', 'AG-2023-001'],
                ['Date of written order to commence work:', '01/01/2023'],
                ['St. date of Start:', '15/01/2023'],
                ['St. date of completion:', '15/07/2023'],
                ['Date of actual completion of work:', '30/06/2023']
            ],
            'bill_items': [
                {
                    'item_no': '1',
                    'description': 'Earthwork in excavation',
                    'unit': 'cum',
                    'quantity_bill': 100.00,
                    'quantity_total': 500.00,
                    'rate': 100.00,
                    'amount': 10000.00,
                    'amount_previous': 40000.00,
                    'amount_total': 50000.00
                },
                {
                    'item_no': '2',
                    'description': 'Cement concrete (1:2:4)',
                    'unit': 'cum',
                    'quantity_bill': 50.00,
                    'quantity_total': 200.00,
                    'rate': 5000.00,
                    'amount': 250000.00,
                    'amount_previous': 750000.00,
                    'amount_total': 1000000.00
                }
            ],
            'deviation_items': [
                {
                    'item_no': '1',
                    'description': 'Additional work as per deviation',
                    'unit': 'LS',
                    'quantity_bill': 1.00,
                    'quantity_total': 1.00,
                    'rate': 10000.00,
                    'amount': 10000.00,
                    'amount_previous': 0.00,
                    'amount_total': 10000.00
                }
            ],
            'extra_items': [
                {
                    'description': 'Extra work as per order no. 123',
                    'amount': 5000.00
                }
            ],
            'payable_amount': '1,265,000.00',
            'amount_words': 'Twelve Lakhs Sixty Five Thousand Only',
            'retention_amount': '126,500.00',
            'tds_deduction': '12,650.00',
            'other_deductions': '5,000.00',
            'net_payable': '1,120,850.00'
        }
        logger.info("Test data created successfully")
        return test_data
    except Exception as e:
        logger.error(f"Error creating test data: {e}")
        raise

def test_template_rendering():
    """Test template rendering with sample data"""
    try:
        logger.info("Starting template rendering test...")
        
        # Create output directory
        output_dir = os.path.join(os.getcwd(), 'test_output')
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")
        
        # Initialize document generator
        logger.info("Initializing DocumentGeneratorV04...")
        doc_gen = DocumentGeneratorV04()
        
        # Set output directory
        doc_gen.output_dir = output_dir
        
        # Generate test data
        logger.info("Generating test data...")
        test_data = create_test_data()
        
        # Generate all documents
        logger.info("Generating documents...")
        generated_files = doc_gen.generate_all_documents(test_data)
        
        if generated_files:
            logger.info(f"Successfully generated {len(generated_files)} files:")
            for file_path in generated_files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path) / 1024  # in KB
                    logger.info(f"- {os.path.basename(file_path)} ({file_size:.2f} KB)")
                else:
                    logger.warning(f"- {file_path} (File not found after generation)")
            
            # Verify output directory contents
            logger.info("\nOutput directory contents:")
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path) / 1024  # in KB
                    logger.info(f"- {file} ({file_size:.2f} KB)")
            
            return True
        else:
            logger.error("No files were generated")
            return False
            
    except Exception as e:
        logger.error(f"Error during template rendering test: {e}", exc_info=True)
        return False
    finally:
        logger.info("Template rendering test completed")

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Starting Template Rendering Test")
    logger.info("=" * 80)
    
    success = test_template_rendering()
    
    logger.info("=" * 80)
    if success:
        logger.info("✅ Template rendering test completed successfully")
    else:
        logger.error("❌ Template rendering test failed")
    logger.info("=" * 80)
    
    sys.exit(0 if success else 1)
