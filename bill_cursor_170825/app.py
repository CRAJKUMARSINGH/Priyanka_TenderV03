import streamlit as st
import pandas as pd
import os
import zipfile
import tempfile
from datetime import datetime
import traceback
from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator
from utils.latex_generator import LaTeXGenerator
from utils.pdf_merger import PDFMerger
from utils.zip_packager import ZipPackager

# Page configuration
st.set_page_config(
    page_title="Infrastructure Billing System",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    """Inject custom CSS for professional appearance with green header design"""
    st.markdown("""
    <style>
    /* Main container styling */
    .main > div {
        padding: 2rem 1rem;
    }
    
    /* Header styling - Green gradient design */
    .header-container {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 50%, #81C784 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        text-align: center;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .header-professional {
        font-size: 1rem;
        text-align: center;
        color: #e8f5e9;
        opacity: 0.85;
        margin-bottom: 0.5rem;
        font-weight: 400;
        font-style: italic;
        letter-spacing: 0.8px;
    }
    
    .header-initiative {
        font-size: 0.9rem;
        text-align: center;
        color: #ffffff;
        opacity: 0.9;
        margin-bottom: 0;
        font-weight: 500;
        background: rgba(255,255,255,0.1);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        display: inline-block;
        margin: 0 auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Upload card styling */
    .upload-card {
        background: #ffffff;
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    
    .upload-card:hover {
        border-color: #45a049;
        background: #f8fff8;
    }
    
    /* Progress styling */
    .progress-container {
        background: #f0f0f0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Results styling */
    .results-container {
        background: #e8f5e9;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #4CAF50;
    }
    
    /* Instructions styling */
    .instructions-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #dee2e6;
    }
    
    .how-to-title {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .how-to-subtitle {
        color: #7f8c8d;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Metrics styling */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    """Display the professional header with crane logo and green gradient"""
    st.markdown("""
    <div class="header-container">
        <div style="text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🏗️</div>
            <div class="header-title">Infrastructure Billing System</div>
            <div class="header-subtitle">Election Commission Compliant Document Generator</div>
            <div class="header-professional">Professional Infrastructure Documentation Solution</div>
            <div style="margin-top: 1.5rem;">
                <div class="header-initiative">
                    Initiative by Mrs. Premlata Jain, Additional Administrative Officer, PWD, Udaipur
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_instructions():
    """Display colorful, user-friendly instructions"""
    st.markdown("""
    <div class="instructions-container">
        <h2 class="how-to-title">🎯 How to Use This System</h2>
        <p class="how-to-subtitle">Simple steps to generate your billing documents in minutes!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Three main steps using Streamlit columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
            <h3>Step 1: Upload</h3>
            <p>Just drag & drop your Excel file or click to browse</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 15px; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
            <h3>Step 2: Wait</h3>
            <p>System automatically creates all your documents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 15px; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📥</div>
            <h3>Step 3: Download</h3>
            <p>Get all documents in one convenient package</p>
        </div>
        """, unsafe_allow_html=True)

def display_expandable_info():
    """Display detailed information in expandable sections"""
    with st.expander("📋 What Your Excel File Should Have"):
        st.markdown("""
        **Title Sheet:** Project details like name, contract number
        
        **Work Order:** Original planned work items
        
        **Bill Quantity:** Actual work completed
        
        **Extra Items:** Any additional work (optional)
        """)
    
    with st.expander("📄 What Documents You'll Get"):
        st.markdown("""
        **Professional Documents:** First Page Summary, Deviation Statement, Bill Scrutiny, Certificates
        
        **Multiple Formats:** 
        - HTML for viewing
        - LaTeX templates for Election Commission compliance
        - Dual PDF versions (HTML-based and LaTeX-based)
        - Excel outputs for each template
        
        **Ready to Submit:** All documents follow government standards
        """)
    
    with st.expander("💡 Quick Tips"):
        st.markdown("""
        **File Size:** Works with files up to 10MB
        
        **Format:** Excel files (.xlsx or .xls)
        
        **Speed:** Processing takes 30-60 seconds
        
        **Security:** All data stays secure on your device
        """)

def process_file(uploaded_file):
    """Process the uploaded Excel file and generate all documents"""
    try:
        # Create progress container
        progress_container = st.container()
        with progress_container:
            st.markdown('<div class="progress-container">', unsafe_allow_html=True)
            progress_bar = st.progress(0)
            status_text = st.empty()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 1: Process Excel file
        status_text.text("📊 Processing Excel file...")
        progress_bar.progress(10)
        
        processor = ExcelProcessor()
        data = processor.process_file(uploaded_file)
        
        if not data:
            st.error("❌ Failed to process Excel file. Please check the file format and try again.")
            return None
        
        progress_bar.progress(25)
        
        # Step 2: Generate HTML documents
        status_text.text("📄 Generating HTML documents...")
        doc_generator = DocumentGenerator()
        html_docs = doc_generator.generate_all_documents(data)
        
        progress_bar.progress(40)
        
        # Step 3: Generate LaTeX documents
        status_text.text("📐 Generating LaTeX templates...")
        latex_generator = LaTeXGenerator()
        latex_docs = latex_generator.process_all_documents(data)
        
        progress_bar.progress(55)
        
        # Step 4: Generate PDFs from HTML
        status_text.text("📑 Converting HTML to PDF...")
        pdf_merger = PDFMerger()
        html_pdfs = pdf_merger.convert_html_to_pdf(html_docs)
        
        progress_bar.progress(70)
        
        # Step 5: Generate PDFs from LaTeX
        status_text.text("📄 Converting LaTeX to PDF...")
        latex_pdfs = pdf_merger.convert_latex_to_pdf(latex_docs)
        
        progress_bar.progress(85)
        
        # Step 6: Generate Excel outputs
        status_text.text("📊 Creating Excel outputs...")
        excel_outputs = doc_generator.generate_excel_outputs(data)
        
        progress_bar.progress(95)
        
        # Step 7: Package everything
        status_text.text("📦 Packaging documents...")
        packager = ZipPackager()
        
        # Generate smart filename with project name and timestamp
        project_name = data.get('project_name', 'Infrastructure_Project')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{project_name}_{timestamp}_Complete_Package.zip"
        
        zip_buffer = packager.create_package(
            html_docs=html_docs,
            latex_docs=latex_docs,
            html_pdfs=html_pdfs,
            latex_pdfs=latex_pdfs,
            excel_outputs=excel_outputs,
            filename=zip_filename
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Celebration animation
        st.balloons()
        
        return {
            'zip_buffer': zip_buffer,
            'filename': zip_filename,
            'html_docs': html_docs,
            'latex_docs': latex_docs,
            'html_pdfs': html_pdfs,
            'latex_pdfs': latex_pdfs,
            'excel_outputs': excel_outputs,
            'data': data
        }
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.error("🔍 Please check your Excel file format and try again.")
        with st.expander("🛠️ Troubleshooting Tips"):
            st.markdown("""
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 1rem;">
            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                <li>Ensure your Excel file has all required sheets with correct names</li>
                <li>Check that data starts from the first row (no empty rows at top)</li>
                <li>Verify column headers match the expected format</li>
                <li>Make sure numeric columns contain only numbers (no text like "Above")</li>
                <li>Try using a test file that worked successfully</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        return None

def display_results(results):
    """Display processing results with metrics and download options"""
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Metrics dashboard
    st.subheader("📊 Processing Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #4CAF50; margin: 0;">📄</h3>
            <h4 style="margin: 0.5rem 0;">HTML Docs</h4>
            <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">{}</p>
        </div>
        """.format(len(results['html_docs'])), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #FF9800; margin: 0;">📐</h3>
            <h4 style="margin: 0.5rem 0;">LaTeX Docs</h4>
            <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">{}</p>
        </div>
        """.format(len(results['latex_docs'])), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #F44336; margin: 0;">📑</h3>
            <h4 style="margin: 0.5rem 0;">PDF Files</h4>
            <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">{}</p>
        </div>
        """.format(len(results['html_pdfs']) + len(results['latex_pdfs'])), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #2196F3; margin: 0;">📊</h3>
            <h4 style="margin: 0.5rem 0;">Excel Files</h4>
            <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">{}</p>
        </div>
        """.format(len(results['excel_outputs'])), unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Tabbed results display
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Download Package", "📄 Documents", "📊 Data Preview", "ℹ️ File Details"])
    
    with tab1:
        st.subheader("🎉 Your Complete Document Package is Ready!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div style="background: #e8f5e9; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #4CAF50;">
                <h4 style="color: #2e7d32; margin-top: 0;">📦 Package Contents:</h4>
                <ul style="color: #388e3c;">
                    <li><strong>HTML Documents:</strong> For web viewing and editing</li>
                    <li><strong>LaTeX Templates:</strong> Election Commission compliant formats</li>
                    <li><strong>Dual PDFs:</strong> Both HTML-based and LaTeX-based versions</li>
                    <li><strong>Excel Outputs:</strong> Spreadsheet versions of all documents</li>
                    <li><strong>Organized Structure:</strong> Folders for easy navigation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Professional download button
            st.download_button(
                label="🚀 Download Complete Package",
                data=results['zip_buffer'],
                file_name=results['filename'],
                mime="application/zip",
                help="Download all generated documents in organized ZIP package"
            )
            
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <span style="background: #4CAF50; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                    ✅ Production Quality
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📋 Generated Documents")
        
        # Display document lists
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**HTML Documents:**")
            for doc_name in results['html_docs'].keys():
                st.markdown(f"• {doc_name}")
            
            st.markdown("**LaTeX Documents:**")
            for doc_name in results['latex_docs'].keys():
                st.markdown(f"• {doc_name}")
        
        with col2:
            st.markdown("**PDF Files (HTML-based):**")
            for doc_name in results['html_pdfs'].keys():
                st.markdown(f"• {doc_name}")
            
            st.markdown("**PDF Files (LaTeX-based):**")
            for doc_name in results['latex_pdfs'].keys():
                st.markdown(f"• {doc_name}")
    
    with tab3:
        st.subheader("👀 Data Preview")
        
        # Display key data points
        data = results['data']
        
        if 'project_info' in data:
            st.markdown("**Project Information:**")
            project_info = data['project_info']
            for key, value in project_info.items():
                st.markdown(f"• **{key}:** {value}")
        
        if 'bill_items' in data and data['bill_items']:
            st.markdown("**Bill Items Summary:**")
            st.markdown(f"• Total Items: {len(data['bill_items'])}")
            if 'total_amount' in data:
                st.markdown(f"• Total Amount: ₹{data['total_amount']:,.2f}")
        
        if 'extra_items' in data and data['extra_items']:
            st.markdown("**Extra Items Summary:**")
            st.markdown(f"• Extra Items: {len(data['extra_items'])}")
    
    with tab4:
        st.subheader("📁 File Details")
        
        st.markdown(f"**Package Name:** {results['filename']}")
        st.markdown(f"**Generated On:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        st.markdown(f"**Total Files:** {len(results['html_docs']) + len(results['latex_docs']) + len(results['html_pdfs']) + len(results['latex_pdfs']) + len(results['excel_outputs'])}")
        
        # File size estimation
        zip_size = len(results['zip_buffer']) / (1024 * 1024)  # Convert to MB
        st.markdown(f"**Package Size:** {zip_size:.2f} MB")

def main():
    """Main application function"""
    # Inject custom CSS
    inject_custom_css()
    
    # Display header
    display_header()
    
    # Display instructions
    display_instructions()
    
    # Display expandable information
    display_expandable_info()
    
    # File upload section
    st.markdown("---")
    st.subheader("📁 Upload Your Excel File")
    
    uploaded_file = st.file_uploader(
        "Choose your Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file containing Title, Work Order, Bill Quantity, and Extra Items sheets",
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # Display file info
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
        st.success(f"✅ File uploaded successfully: {uploaded_file.name} ({file_size:.2f} MB)")
        
        # Process button
        if st.button("🚀 Generate Documents", type="primary", use_container_width=True):
            with st.spinner("Processing your file..."):
                results = process_file(uploaded_file)
                
                if results:
                    # Store results in session state for persistence
                    st.session_state['results'] = results
    
    # Display results if available
    if 'results' in st.session_state:
        st.markdown("---")
        display_results(st.session_state['results'])
    
    # Sidebar with additional information
    with st.sidebar:
        st.markdown("### 🏗️ System Information")
        st.markdown("""
        **Version:** 2.0.0  
        **Last Updated:** August 2025  
        **Compliance:** Election Commission Standards  
        **Formats:** HTML, LaTeX, PDF, Excel
        """)
        
        st.markdown("### 📞 Support")
        st.markdown("""
        For technical support or questions about this system, please contact the PWD office.
        """)
        
        st.markdown("### 🎯 Features")
        st.markdown("""
        ✅ Dual PDF Generation  
        ✅ LaTeX Templates  
        ✅ Excel Outputs  
        ✅ Smart Packaging  
        ✅ Error Recovery  
        ✅ Professional Styling
        """)

if __name__ == "__main__":
    main()
