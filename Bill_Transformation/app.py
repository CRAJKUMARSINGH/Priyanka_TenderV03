import streamlit as st
import pandas as pd
import os
import tempfile
import zipfile
import io
from datetime import datetime
import traceback
import openpyxl
from excel_processor_v01 import ExcelProcessorV01
from document_generator_v04 import DocumentGeneratorV04
from custom_utils.utils import setup_wkhtmltopdf, resolve_logo_url

# Page setup
st.set_page_config(
    page_title="Advanced Bill Generator V04",
    page_icon="📋",
    layout="wide"
)

def main():
    st.title("📋 Advanced Bill Generator V04")
    st.markdown("Professional contractor billing and document generation system")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Output format selection
        st.subheader("Output Formats")
        generate_html = st.checkbox("HTML Documents", value=True)
        generate_pdf = st.checkbox("PDF Documents", value=True)
        generate_docx = st.checkbox("DOCX Documents", value=True)
        generate_latex = st.checkbox("LaTeX Documents", value=False)
        
        # Font configuration
        st.subheader("Display Options")
        reverse_font = st.checkbox("Reverse Font Colors", value=False)
        
        # Premium percentage
        st.subheader("Bill Configuration")
        premium_percentage = st.number_input(
            "Premium Percentage (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=10.0,
            step=0.1
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 File Upload")
        
        # File upload with multiple file support
        uploaded_files = st.file_uploader(
            "Upload Excel Bill Files (V01 Format)",
            type=['xlsx', 'xlsm', 'xls'],
            accept_multiple_files=True,
            help="Upload up to 15 contractor bills in V01 format for batch transformation to V04"
        )
        
        if uploaded_files:
            # Limit to 15 files maximum
            if len(uploaded_files) > 15:
                st.warning("⚠️ Maximum 15 files allowed. Only processing first 15 files.")
                uploaded_files = uploaded_files[:15]
            
            st.success(f"✅ {len(uploaded_files)} file(s) loaded")
            
            # Show file info
            with st.expander("📊 Files Information"):
                for i, uploaded_file in enumerate(uploaded_files, 1):
                    st.write(f"**{i}. {uploaded_file.name}**")
                    try:
                        # Load workbook to show sheet names
                        workbook = openpyxl.load_workbook(uploaded_file, read_only=True)
                        st.write(f"   Sheets: {', '.join(workbook.sheetnames)}")
                        workbook.close()
                    except Exception as e:
                        st.write(f"   Error: {e}")
                    uploaded_file.seek(0)  # Reset file pointer
    
    with col2:
        st.header("🚀 Actions")
        
        if uploaded_files:
            if st.button("🔄 Process Bills", type="primary", use_container_width=True):
                process_bills_batch(
                    uploaded_files, 
                    premium_percentage,
                    reverse_font,
                    generate_html,
                    generate_pdf,
                    generate_docx,
                    generate_latex
                )
            
            if st.button("🧪 Test Processing", use_container_width=True):
                test_processing_batch(uploaded_files)
    
    # System status
    st.header("🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Check wkhtmltopdf
        wkhtmltopdf_status = setup_wkhtmltopdf()
        if wkhtmltopdf_status:
            st.success("✅ PDF Generation Available")
        else:
            st.warning("⚠️ PDF Generation Limited")
    
    with col2:
        # Check templates
        templates_dir = os.path.join(os.getcwd(), 'templates')
        if os.path.exists(templates_dir):
            template_count = len([f for f in os.listdir(templates_dir) if f.endswith('.html')])
            st.success(f"✅ {template_count} Templates Found")
        else:
            st.error("❌ Templates Directory Missing")
    
    with col3:
        # System info
        st.info(f"📅 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def process_bills_batch(uploaded_files, premium_percentage, reverse_font, gen_html, gen_pdf, gen_docx, gen_latex):
    """Process multiple uploaded bill files in batch"""
    
    total_files = len(uploaded_files)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_generated_files = []
    processed_data = []
    failed_files = []
    
    try:
        st.info(f"🔄 Starting batch processing of {total_files} files...")
        
        for file_idx, uploaded_file in enumerate(uploaded_files):
            try:
                # Update progress
                file_progress = (file_idx / total_files) * 100
                status_text.text(f"Processing file {file_idx + 1}/{total_files}: {uploaded_file.name}")
                progress_bar.progress(int(file_progress))
                
                # Step 1: Process Excel file
                processor = ExcelProcessorV01()
                data = processor.process_excel(uploaded_file)
                
                # Add premium percentage and file info to data
                data['premium_percentage'] = premium_percentage
                data['source_filename'] = uploaded_file.name
                data['file_index'] = file_idx + 1
                
                # Step 2: Generate documents
                generator = DocumentGeneratorV04()
                
                # Configure generator based on user selections
                generator.generate_html = gen_html
                generator.generate_pdf = gen_pdf
                generator.generate_docx = gen_docx
                generator.generate_latex = gen_latex
                
                # Create unique output directory for this file
                generator.output_dir = tempfile.mkdtemp(prefix=f'bill_v04_{file_idx+1}_')
                
                files = generator.generate_all_documents(data, reverse_font)
                
                # Rename files to include bill identifier
                renamed_files = []
                bill_id = data.get('bill_number', f'bill_{file_idx+1}')
                for file_path in files:
                    if os.path.exists(file_path):
                        file_ext = os.path.splitext(file_path)[1]
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        new_name = f"{bill_id}_{base_name}{file_ext}"
                        new_path = os.path.join(os.path.dirname(file_path), new_name)
                        os.rename(file_path, new_path)
                        renamed_files.append(new_path)
                
                all_generated_files.extend(renamed_files)
                processed_data.append(data)
                
                st.success(f"✅ File {file_idx + 1} processed: {uploaded_file.name}")
                
            except Exception as e:
                failed_files.append({'name': uploaded_file.name, 'error': str(e)})
                st.error(f"❌ Failed to process {uploaded_file.name}: {str(e)}")
                continue
        
        # Final progress update
        progress_bar.progress(100)
        status_text.text("✅ Batch processing completed!")
        
        # Display batch results
        display_batch_results(all_generated_files, processed_data, failed_files)
        
    except Exception as e:
        st.error(f"❌ Error in batch processing: {str(e)}")
        st.error("**Full error traceback:**")
        st.code(traceback.format_exc())

def test_processing_batch(uploaded_files):
    """Test batch file processing without full generation"""
    
    with st.spinner("Testing batch file processing..."):
        try:
            results = []
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    processor = ExcelProcessorV01()
                    data = processor.process_excel(uploaded_file)
                    results.append({
                        'file': uploaded_file.name,
                        'status': 'Success',
                        'data': data
                    })
                except Exception as e:
                    results.append({
                        'file': uploaded_file.name,
                        'status': 'Failed',
                        'error': str(e)
                    })
            
            # Show results summary
            success_count = sum(1 for r in results if r['status'] == 'Success')
            st.success(f"✅ Batch test completed: {success_count}/{len(uploaded_files)} files processed successfully")
            
            # Show detailed results
            with st.expander("🔍 Detailed Test Results"):
                for result in results:
                    if result['status'] == 'Success':
                        st.write(f"**{result['file']}** - ✅ Success")
                        st.json(result['data'], expanded=False)
                    else:
                        st.write(f"**{result['file']}** - ❌ Failed: {result['error']}")
                        
        except Exception as e:
            st.error(f"❌ Batch test failed: {str(e)}")
            st.error("**Error details:**")
            st.code(traceback.format_exc())

def create_zip_bundle(file_paths):
    """Create a ZIP bundle of all files"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                zip_file.write(file_path, filename)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def display_batch_results(all_files, processed_data, failed_files):
    """Display batch processing results and download options"""
    
    st.header("📋 Batch Processing Results")
    
    # Summary statistics
    total_files = len(processed_data) + len(failed_files)
    successful_files = len(processed_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", total_files)
    
    with col2:
        st.metric("Successful", successful_files, delta=f"{(successful_files/total_files*100):.0f}%" if total_files > 0 else "0%")
    
    with col3:
        st.metric("Failed", len(failed_files), delta=f"-{(len(failed_files)/total_files*100):.0f}%" if total_files > 0 else "0%")
    
    with col4:
        st.metric("Documents Generated", len(all_files))
    
    # Show failed files if any
    if failed_files:
        with st.expander("❌ Failed Files"):
            for failed in failed_files:
                st.error(f"**{failed['name']}**: {failed['error']}")
    
    # Show successful processing summary
    if processed_data:
        with st.expander("✅ Successfully Processed Files"):
            for data in processed_data:
                st.write(f"**{data.get('source_filename', 'Unknown')}** - Bill: {data.get('bill_number', 'N/A')} - Amount: ₹{data.get('total_amount', 0):,.2f}")
    
    # Download section
    if all_files:
        st.subheader("⬇️ Download Results")
        
        # Create master ZIP with all files
        zip_buffer = create_zip_bundle(all_files)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"batch_bills_v04_{timestamp}.zip"
        
        st.download_button(
            label=f"📦 Download All Files ({len(all_files)} documents)",
            data=zip_buffer,
            file_name=zip_filename,
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
        
        # File list
        with st.expander("📁 Generated Files List"):
            for file_path in all_files:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    st.write(f"• **{filename}** ({file_size:,} bytes)")
    
    else:
        st.warning("No files were generated. Please check the error messages above.")

def display_results(files, zip_buffer, data):
    """Display processing results and download options"""
    
    st.header("📋 Processing Results")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Files Generated", len(files))
    
    with col2:
        total_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
        st.metric("Total Size", f"{total_size/1024:.1f} KB")
    
    with col3:
        html_files = len([f for f in files if f.endswith('.html')])
        st.metric("HTML Files", html_files)
    
    with col4:
        pdf_files = len([f for f in files if f.endswith('.pdf')])
        st.metric("PDF Files", pdf_files)
    
    # File list
    with st.expander("📁 Generated Files"):
        for file_path in files:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                st.write(f"• **{filename}** ({file_size:,} bytes)")
    
    # Download section
    st.subheader("⬇️ Download Results")
    
    # Main ZIP download
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"bill_v04_{timestamp}.zip"
    
    st.download_button(
        label="📦 Download All Files (ZIP)",
        data=zip_buffer,
        file_name=zip_filename,
        mime="application/zip",
        type="primary",
        use_container_width=True
    )
    
    # Individual file downloads
    st.subheader("📄 Individual Downloads")
    
    cols = st.columns(3)
    col_idx = 0
    
    for file_path in files:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            with cols[col_idx % 3]:
                st.download_button(
                    label=f"📄 {filename}",
                    data=file_data,
                    file_name=filename,
                    mime=get_mime_type(filename),
                    use_container_width=True
                )
            
            col_idx += 1

def get_mime_type(filename):
    """Get MIME type for file"""
    ext = os.path.splitext(filename)[1].lower()
    mime_types = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.html': 'text/html',
        '.zip': 'application/zip',
        '.tex': 'application/x-latex'
    }
    return mime_types.get(ext, 'application/octet-stream')

if __name__ == "__main__":
    # Setup wkhtmltopdf
    wkhtmltopdf_config = setup_wkhtmltopdf()
    
    main()
