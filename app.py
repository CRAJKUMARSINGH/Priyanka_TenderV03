import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import tempfile
import logging
from pathlib import Path

DB_PATH = Path(__file__).parent / "bidder_database.json"

# Import custom modules
from theme import apply_custom_css
from ui_components import create_header, create_footer, show_balloons, create_info_card
from tender_processor import TenderProcessor
from excel_parser import ExcelParser
from bidder_manager import BidderManager
from report_generator import ReportGenerator
from document_generator import DocumentGenerator
from comparative_statement_generator import ComparativeStatementGenerator
from letter_acceptance_generator import LetterAcceptanceGenerator
from work_order_generator import WorkOrderGenerator
from scrutiny_sheet_generator import ScrutinySheetGenerator
from date_utils import DateUtils
from pdf_generator import PDFGenerator
from latex_pdf_generator import LatexPDFGenerator
from zip_generator import ZipGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Page configuration
st.set_page_config(
    page_title="Tender Processing System",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

def main():
    """Main application function."""
    
    create_header()
    
    if 'current_work' not in st.session_state:
        st.session_state.current_work = None
    if 'bidders' not in st.session_state:
        st.session_state.bidders = []
    if 'bidder_manager' not in st.session_state:
        st.session_state.bidder_manager = BidderManager()
    
    st.sidebar.title("📋 Navigation")
    
    operation = st.sidebar.radio(
        "Select Operation:",
        [
            "📄 Upload NIT Document", 
            "👥 Manage Bidders", 
            "📊 Generate Reports",
            "📝 Generate Documents"
        ]
    )
    
    if operation == "📄 Upload NIT Document":
        handle_nit_upload()
    elif operation == "👥 Manage Bidders":
        handle_bidder_management()
    elif operation == "📊 Generate Reports":
        handle_report_generation()
    elif operation == "📝 Generate Documents":
        handle_document_generation()
    
    create_footer()

def handle_nit_upload():
    """Handle NIT document upload and processing."""
    st.header("📄 Upload NIT Document")
    
    create_info_card(
        "NIT Document Upload", 
        "Upload your Notice Inviting Tender (NIT) Excel file to extract work details and estimated costs. "
        "The system supports multiple date formats and will automatically parse the tender information.",
        "📄"
    )
    
    uploaded_file = st.file_uploader(
        "Choose NIT Excel file", 
        type=['xlsx', 'xls'],
        help="Upload the official NIT Excel document"
    )
    
    if uploaded_file is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            parser = ExcelParser()
            work_data = parser.parse_nit_excel(tmp_file_path)
            
            os.unlink(tmp_file_path)
            
            if work_data:
                st.session_state.current_work = work_data
                st.success("✅ NIT document uploaded and parsed successfully!")
                st.rerun()
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 NIT Information")
                    st.write(f"**Work Package:** {work_data['work_name']}")
                    st.write(f"**NIT Number:** {work_data['nit_number']}")
                    st.write(f"**Total Works:** {work_data.get('total_works', 1)}")
                    st.write(f"**Total Estimated Cost:** ₹{work_data['estimated_cost']:,.2f}")
                    st.write(f"**Total Earnest Money:** ₹{work_data['earnest_money']:,.2f}")
                
                with col2:
                    st.subheader("📅 Timeline Information")
                    st.write(f"**NIT Date:** {work_data.get('nit_date', 'Not found')}")
                    st.write(f"**Receipt Date:** {work_data.get('receipt_date', 'Not found')}")
                    st.write(f"**Opening Date:** {work_data.get('opening_date', 'Not found')}")
                    st.write(f"**Max Completion Time:** {work_data.get('time_completion', 6)} months")
                
                if work_data.get('works') and len(work_data['works']) > 1:
                    st.subheader("📋 Individual Works Details")
                    
                    works_df = pd.DataFrame(work_data['works'])
                    works_df['estimated_cost_display'] = works_df['estimated_cost'].apply(lambda x: f"₹{x:,.0f}")
                    works_df['earnest_money_display'] = works_df['earnest_money'].apply(lambda x: f"₹{x:,.0f}")
                    
                    display_df = works_df[['item_no', 'name', 'estimated_cost_display', 'time_completion', 'earnest_money_display']]
                    display_df.columns = ['Item No.', 'Work Name', 'Estimated Cost', 'Time (Months)', 'Earnest Money']
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    st.info(f"💡 This NIT contains {len(work_data['works'])} individual works. Go to 'Manage Bidders' to select a specific work for bidding.")
                elif work_data.get('works') and len(work_data['works']) == 1:
                    st.subheader("📋 Work Details")
                    work = work_data['works'][0]
                    st.write(f"**Work Name:** {work['name']}")
                    st.write(f"**Estimated Cost:** ₹{work['estimated_cost']:,.2f}")
                    st.write(f"**Time of Completion:** {work['time_completion']} months")
                    st.write(f"**Earnest Money:** ₹{work['earnest_money']:,.2f}")
                    st.info("💡 Go to 'Manage Bidders' to add bidders for this work.")
                
                show_balloons()
            else:
                st.error("❌ Failed to parse NIT document. Please check the file format.")
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            logging.error(f"Error processing NIT file: {e}")

def handle_bidder_management():
    """Handle bidder management operations with work selection."""
    st.header("👥 Manage Bidders")
    
    work_data = st.session_state.get("current_work")
    if work_data is None:
        st.warning("⚠️ Please upload a NIT document first.")
        return
    
    selected_work = None
    if st.session_state.current_work.get('works') and len(st.session_state.current_work['works']) > 1:
        st.subheader("📋 Step 1: Select Work for Bidding")
        
        work_options = []
        for work in st.session_state.current_work['works']:
            work_options.append(f"Item {work['item_no']}: {work['name']} (₹{work['estimated_cost']:,.0f})")
        
        selected_work_index = st.selectbox(
            "Select which work to process bids for:",
            range(len(work_options)),
            format_func=lambda x: work_options[x],
            help="Choose the specific work item for which you want to add bidders"
        )
        
        selected_work = st.session_state.current_work['works'][selected_work_index]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Selected Work:** {selected_work['name']}")
            st.write(f"**Item Number:** {selected_work['item_no']}")
            st.write(f"**Estimated Cost:** ₹{selected_work['estimated_cost']:,.2f}")
        with col2:
            st.write(f"**Time Completion:** {selected_work['time_completion']} months")
            st.write(f"**Earnest Money:** ₹{selected_work['earnest_money']:,.2f}")
        
        st.markdown("---")
    else:
        selected_work = st.session_state.current_work['works'][0] if st.session_state.current_work.get('works') else {
            'item_no': 1,
            'name': st.session_state.current_work['work_name'],
            'estimated_cost': st.session_state.current_work['estimated_cost'],
            'earnest_money': st.session_state.current_work['earnest_money'],
            'time_completion': st.session_state.current_work.get('time_completion', 6)
        }
    
    if not selected_work:
        st.error("❌ No work selected or available.")
        return
    
    bidder_database = {}
    try:
        with open('bidder_database.json', 'r', encoding='utf-8') as f:
            bidder_database = json.load(f)
    except Exception as e:
        st.error(f"❌ Error loading bidder database: {str(e)}")
        return
    
    st.info(f"📋 Available bidders in database: {len(bidder_database)}")
    
    st.subheader("📊 Step 2: Select Number of Bidders")
    num_bidders = st.number_input(
        f"How many bidders participated for {selected_work['name']}?", 
        min_value=1, 
        max_value=20, 
        value=3,
        help="Select the number of bidders who submitted tenders for this work"
    )
    
    if num_bidders:
        st.subheader("👥 Step 3: Add Bidders and Enter Percentages")
        
        if 'bidder_inputs' not in st.session_state:
            st.session_state.bidder_inputs = {}
        
        bidder_data_list = []
        all_valid = True
        
        for i in range(num_bidders):
            st.markdown(f"### Bidder {i+1}")
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                bidder_source = st.radio(
                    f"Bidder {i+1} source:",
                    ["Select from database", "Add new bidder"],
                    key=f"source_{i}",
                    horizontal=True
                )
                
                if bidder_source == "Select from database":
                    selected_bidder = st.selectbox(
                        f"Select Bidder {i+1}:",
                        options=[""] + list(bidder_database.keys()),
                        key=f"bidder_select_{i}",
                        help="Choose from registered bidders"
                    )
                    
                    bidder_name = selected_bidder
                    bidder_address = bidder_database.get(selected_bidder, {}).get('address', '') if selected_bidder else ''
                    
                    if selected_bidder and selected_bidder in bidder_database:
                        st.caption(f"📍 Address: {bidder_address}")
                
                else:
                    bidder_name = st.text_input(
                        f"Bidder {i+1} Name:",
                        key=f"new_bidder_name_{i}",
                        placeholder="Enter bidder company name"
                    )
                    bidder_address = st.text_input(
                        f"Bidder {i+1} Address:",
                        key=f"new_bidder_address_{i}",
                        placeholder="Enter complete address"
                    )
            
            with col2:
                percentage_str = st.text_input(
                    f"Percentage (%):",
                    placeholder="e.g., -5.50",
                    key=f"percentage_{i}",
                    help="Enter % above (+) or below (-) estimate"
                )
            
            with col3:
                if bidder_name and bidder_address and percentage_str:
                    try:
                        percentage = float(percentage_str)
                        if -99.99 <= percentage <= 99.99:
                            processor = TenderProcessor()
                            bid_amount = processor.calculate_bid_amount(selected_work['estimated_cost'], percentage)
                            
                            st.metric("Bid Amount", f"₹{bid_amount:,.0f}")
                            st.caption(f"{percentage:+.2f}% of ₹{selected_work['estimated_cost']:,.0f}")
                            
                            bidder_data = {
                                'name': bidder_name,
                                'address': bidder_address,
                                'percentage': percentage,
                                'bid_amount': bid_amount,
                                'earnest_money': selected_work['earnest_money'],
                                'date_added': DateUtils().get_current_date(),
                                'work_item': selected_work['item_no'],
                                'work_name': selected_work['name'],
                                'estimated_cost': selected_work['estimated_cost']
                            }
                            bidder_data_list.append(bidder_data)
                        else:
                            st.error("❌ Percentage must be between -99.99% and +99.99%")
                            all_valid = False
                    except ValueError:
                        st.error("❌ Please enter a valid percentage value")
                        all_valid = False
                elif bidder_name or percentage_str:
                    all_valid = False
            
            st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Add All Bidders", type="primary", disabled=not all_valid or len(bidder_data_list) != num_bidders):
                st.session_state.bidders = bidder_data_list
                
                for bidder_data in bidder_data_list:
                    if bidder_data['name'] in bidder_database:
                        bidder_database[bidder_data['name']]['last_used'] = DateUtils().get_current_date()
                    else:
                        bidder_database[bidder_data['name']] = {
                            'address': bidder_data['address'],
                            'date_added': DateUtils().get_current_date(),
                            'last_used': DateUtils().get_current_date(),
                            'total_tenders': 1
                        }
                
                try:
                    with open('bidder_database.json', 'w', encoding='utf-8') as f:
                        json.dump(bidder_database, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    st.warning(f"⚠️ Could not update bidder database: {str(e)}")
                
                st.success(f"✅ Added {len(bidder_data_list)} bidders successfully!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset All", type="secondary"):
                st.session_state.bidders = []
                if 'bidder_inputs' in st.session_state:
                    del st.session_state.bidder_inputs
                st.success("✅ Reset all bidder selections")
                st.rerun()
    
    if st.session_state.bidders:
        st.subheader("📊 Current Selected Bidders")
        
        df_data = []
        for i, bidder in enumerate(st.session_state.bidders):
            df_data.append({
                'S.No.': i + 1,
                'Bidder Name': bidder['name'],
                'Address': bidder.get('address', 'N/A'),
                'Percentage (%)': f"{bidder['percentage']:+.2f}%",
                'Bid Amount (₹)': f"₹{bidder['bid_amount']:,.2f}",
                'Earnest Money (₹)': f"₹{bidder['earnest_money']}"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        sorted_bidders = sorted(st.session_state.bidders, key=lambda x: x['bid_amount'])
        l1_bidder = sorted_bidders[0]
        st.success(f"🥇 L1 (Lowest) Bidder: {l1_bidder['name']} - ₹{l1_bidder['bid_amount']:,.2f} ({l1_bidder['percentage']:+.2f}%)")
        
        if st.button("🗑️ Clear All Bidders", type="secondary"):
            st.session_state.bidders = []
            st.success("✅ Cleared all bidders")
            st.rerun()

def handle_report_generation():
    """Handle report generation with simultaneous generation and download."""
    st.header("📊 Generate Reports")
    
    if not st.session_state.current_work or not st.session_state.bidders:
        st.warning("⚠️ Please upload NIT document and add bidders first.")
        return
    
    st.subheader("🚀 Generate All Reports Simultaneously")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📦 Generate All Reports", type="primary", help="Generate all reports at once"):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                pdf_gen = PDFGenerator()
                doc_gen = DocumentGenerator()
                
                generated_files = {}
                
                status_text.text("Generating Comparative Statement PDF...")
                progress_bar.progress(20)
                comp_pdf = pdf_gen.generate_comparative_statement_pdf(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_files['comparative_statement_pdf'] = {
                    'content': comp_pdf,
                    'filename': f"comparative_statement_{st.session_state.current_work['nit_number']}.pdf",
                    'mime': "application/pdf"
                }
                
                status_text.text("Generating Comparative Statement DOC...")
                progress_bar.progress(40)
                comp_doc = doc_gen.generate_comparative_statement_doc(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_files['comparative_statement_doc'] = {
                    'content': comp_doc,
                    'filename': f"comparative_statement_{st.session_state.current_work['nit_number']}.docx",
                    'mime': "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                }
                
                status_text.text("Generating Scrutiny Sheet PDF...")
                progress_bar.progress(60)
                scrutiny_pdf = pdf_gen.generate_scrutiny_sheet_pdf(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_files['scrutiny_sheet_pdf'] = {
                    'content': scrutiny_pdf,
                    'filename': f"scrutiny_sheet_{st.session_state.current_work['nit_number']}.pdf",
                    'mime': "application/pdf"
                }
                
                status_text.text("Generating Scrutiny Sheet DOC...")
                progress_bar.progress(80)
                scrutiny_doc = doc_gen.generate_scrutiny_sheet_doc(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_files['scrutiny_sheet_doc'] = {
                    'content': scrutiny_doc,
                    'filename': f"scrutiny_sheet_{st.session_state.current_work['nit_number']}.docx",
                    'mime': "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                }
                
                progress_bar.progress(100)
                status_text.text("All reports generated successfully!")
                
                st.success("✅ All reports generated simultaneously in PDF and DOC formats!")
                
                st.session_state.generated_reports = generated_files
                
                st.subheader("📥 Download Generated Reports")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Comparative Statement**")
                    st.download_button(
                        label="📋 Download PDF",
                        data=generated_files['comparative_statement_pdf']['content'],
                        file_name=generated_files['comparative_statement_pdf']['filename'],
                        mime="application/pdf",
                        key="download_comp_pdf"
                    )
                    st.download_button(
                        label="📋 Download DOC",
                        data=generated_files['comparative_statement_doc']['content'],
                        file_name=generated_files['comparative_statement_doc']['filename'],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_comp_doc"
                    )
                
                with col_b:
                    st.markdown("**Scrutiny Sheet**")
                    st.download_button(
                        label="🔍 Download PDF",
                        data=generated_files['scrutiny_sheet_pdf']['content'],
                        file_name=generated_files['scrutiny_sheet_pdf']['filename'],
                        mime="application/pdf",
                        key="download_scrutiny_pdf"
                    )
                    st.download_button(
                        label="🔍 Download DOC",
                        data=generated_files['scrutiny_sheet_doc']['content'],
                        file_name=generated_files['scrutiny_sheet_doc']['filename'],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_scrutiny_doc"
                    )
                
            except Exception as e:
                st.error(f"❌ Error in bulk report generation: {str(e)}")
                logging.error(f"Error in bulk report generation: {e}")
    # ... (rest of handle_report_generation() continues as previously provided)

def handle_report_generation():
    """Handle report generation with simultaneous generation and download."""
    st.header("📊 Generate Reports")
    
    if not st.session_state.current_work or not st.session_state.bidders:
        st.warning("⚠️ Please upload NIT document and add bidders first.")
        return
    
    st.subheader("🚀 Generate All Reports Simultaneously")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📦 Generate All Reports", type="primary", help="Generate all reports at once"):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                pdf_gen = PDFGenerator()
                doc_gen = DocumentGenerator()
                
                generated_files = {}
                
                status_text.text("Generating Comparative Statement PDF...")
                progress_bar.progress(20)
                comp_pdf = pdf_gen.generate_comparative_statement_pdf(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_files['comparative_statement_pdf'] = {
                    'content': comp_pdf,
                    'filename': f"comparative_statement_{st.session_state.current_work['nit_number']}.pdf",
                    'mime': "application/pdf"
                }
                
                status_text.text("Generating Comparative Statement DOC...")
                progress_bar.progress(40)
                comp_doc = doc_gen.generate_comparative_statement_doc(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_files['comparative_statement_doc'] = {
                    'content': comp_doc,
                    'filename': f"comparative_statement_{st.session_state.current_work['nit_number']}.docx",
                    'mime': "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                }
                
                status_text.text("Generating Scrutiny Sheet PDF...")
                progress_bar.progress(60)
                scrutiny_pdf = pdf_gen.generate_scrutiny_sheet_pdf(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_files['scrutiny_sheet_pdf'] = {
                    'content': scrutiny_pdf,
                    'filename': f"scrutiny_sheet_{st.session_state.current_work['nit_number']}.pdf",
                    'mime': "application/pdf"
                }
                
                status_text.text("Generating Scrutiny Sheet DOC...")
                progress_bar.progress(80)
                scrutiny_doc = doc_gen.generate_scrutiny_sheet_doc(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_files['scrutiny_sheet_doc'] = {
                    'content': scrutiny_doc,
                    'filename': f"scrutiny_sheet_{st.session_state.current_work['nit_number']}.docx",
                    'mime': "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                }
                
                progress_bar.progress(100)
                status_text.text("All reports generated successfully!")
                
                st.success("✅ All reports generated simultaneously in PDF and DOC formats!")
                
                st.session_state.generated_reports = generated_files
                
                st.subheader("📥 Download Generated Reports")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Comparative Statement**")
                    st.download_button(
                        label="📋 Download PDF",
                        data=generated_files['comparative_statement_pdf']['content'],
                        file_name=generated_files['comparative_statement_pdf']['filename'],
                        mime="application/pdf",
                        key="download_comp_pdf"
                    )
                    st.download_button(
                        label="📋 Download DOC",
                        data=generated_files['comparative_statement_doc']['content'],
                        file_name=generated_files['comparative_statement_doc']['filename'],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_comp_doc"
                    )
                
                with col_b:
                    st.markdown("**Scrutiny Sheet**")
                    st.download_button(
                        label="🔍 Download PDF",
                        data=generated_files['scrutiny_sheet_pdf']['content'],
                        file_name=generated_files['scrutiny_sheet_pdf']['filename'],
                        mime="application/pdf",
                        key="download_scrutiny_pdf"
                    )
                    st.download_button(
                        label="🔍 Download DOC",
                        data=generated_files['scrutiny_sheet_doc']['content'],
                        file_name=generated_files['scrutiny_sheet_doc']['filename'],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_scrutiny_doc"
                    )
                
            except Exception as e:
                st.error(f"❌ Error in bulk report generation: {str(e)}")
                logging.error(f"Error in bulk report generation: {e}")
    
    with col2:
        if st.button("📄 Generate All Documents", type="primary", help="Generate all official documents at once"):
            try:
                progress_bar2 = st.progress(0)
                status_text2 = st.empty()
                
                pdf_gen = PDFGenerator()
                doc_gen = DocumentGenerator()
                
                # Prepare work_info for document generation
                work_data = st.session_state.current_work
                work_info = {
                    'name': work_data.get('work_name', 'Unknown Work'),
                    'nit_number': work_data.get('nit_number', 'Unknown NIT'),
                    'estimated_cost': work_data.get('estimated_cost', 0),
                    'earnest_money': work_data.get('earnest_money', 0),
                    'time_completion': work_data.get('time_completion', 6),
                    'time_of_completion': work_data.get('time_completion', 6),  # Added for compatibility
                    'nit_date': work_data.get('nit_date', 'Not found'),
                    'receipt_date': work_data.get('receipt_date', 'Not found'),
                    'opening_date': work_data.get('opening_date', 'Not found'),
                    'date': work_data.get('nit_date', 'Not found')  # Added for compatibility
                }
                # If there's a works list, use the first work's details
                if work_data.get('works') and len(work_data['works']) > 0:
                    work_info.update({
                        'name': work_data['works'][0]['name'],
                        'item_no': work_data['works'][0]['item_no'],
                        'estimated_cost': work_data['works'][0]['estimated_cost'],
                        'earnest_money': work_data['works'][0]['earnest_money'],
                        'time_completion': work_data['works'][0]['time_completion'],
                        'time_of_completion': work_data['works'][0]['time_completion']  # Added for compatibility
                    })
                
                # Update current_work with work_info
                st.session_state.current_work['work_info'] = work_info
                
                generated_docs = {}
                
                status_text2.text("Generating Letter of Acceptance PDF...")
                progress_bar2.progress(25)
                loa_pdf = pdf_gen.generate_letter_of_acceptance_pdf(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_docs['letter_of_acceptance_pdf'] = {
                    'content': loa_pdf,
                    'filename': f"letter_of_acceptance_{st.session_state.current_work['nit_number']}.pdf",
                    'mime': "application/pdf"
                }
                
                status_text2.text("Generating Letter of Acceptance DOC...")
                progress_bar2.progress(50)
                loa_doc = doc_gen.generate_letter_of_acceptance_doc(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_docs['letter_of_acceptance_doc'] = {
                    'content': loa_doc,
                    'filename': f"letter_of_acceptance_{st.session_state.current_work['nit_number']}.docx",
                    'mime': "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                }
                
                status_text2.text("Generating Work Order PDF...")
                progress_bar2.progress(75)
                wo_pdf = pdf_gen.generate_work_order_pdf(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_docs['work_order_pdf'] = {
                    'content': wo_pdf,
                    'filename': f"work_order_{st.session_state.current_work['nit_number']}.pdf",
                    'mime': "application/pdf"
                }
                
                status_text2.text("Generating Work Order DOC...")
                progress_bar2.progress(100)
                wo_doc = doc_gen.generate_work_order_doc(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                generated_docs['work_order_doc'] = {
                    'content': wo_doc,
                    'filename': f"work_order_{st.session_state.current_work['nit_number']}.docx",
                    'mime': "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                }
                
                status_text2.text("All documents generated successfully!")
                
                st.success("✅ All documents generated simultaneously in PDF and DOC formats!")
                
                st.session_state.generated_documents = generated_docs
                
                st.subheader("📥 Download Generated Documents")
                
                col_x, col_y = st.columns(2)
                
                with col_x:
                    st.markdown("**Letter of Acceptance**")
                    st.download_button(
                        label="📄 Download PDF",
                        data=generated_docs['letter_of_acceptance_pdf']['content'],
                        file_name=generated_docs['letter_of_acceptance_pdf']['filename'],
                        mime="application/pdf",
                        key="download_loa_pdf"
                    )
                    st.download_button(
                        label="📄 Download DOC",
                        data=generated_docs['letter_of_acceptance_doc']['content'],
                        file_name=generated_docs['letter_of_acceptance_doc']['filename'],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_loa_doc"
                    )
                
                with col_y:
                    st.markdown("**Work Order**")
                    st.download_button(
                        label="📋 Download PDF",
                        data=generated_docs['work_order_pdf']['content'],
                        file_name=generated_docs['work_order_pdf']['filename'],
                        mime="application/pdf",
                        key="download_wo_pdf"
                    )
                    st.download_button(
                        label="📋 Download DOC",
                        data=generated_docs['work_order_doc']['content'],
                        file_name=generated_docs['work_order_doc']['filename'],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_wo_doc"
                    )
                
            except Exception as e:
                st.error(f"❌ Error in bulk document generation: {str(e)}")
                logging.error(f"Error in bulk document generation: {e}")
    
    st.markdown("---")
    
    st.subheader("🎯 Generate Individual Reports")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("📋 Generate Comparative Statement", type="secondary"):
            try:
                comp_gen = ComparativeStatementGenerator()
                html_content = comp_gen.generate_comparative_statement(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                
                st.success("✅ Comparative statement generated!")
                
                st.download_button(
                    label="📥 Download Comparative Statement",
                    data=html_content,
                    file_name=f"comparative_statement_{st.session_state.current_work['nit_number']}.html",
                    mime="text/html",
                    key="single_comp"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating comparative statement: {str(e)}")
                logging.error(f"Error generating comparative statement: {e}")
    
    with col4:
        if st.button("📊 Generate Detailed Report", type="secondary"):
            try:
                # Prepare work_info for detailed report to ensure time_of_completion
                work_data = st.session_state.current_work
                work_info = {
                    'name': work_data.get('work_name', 'Unknown Work'),
                    'nit_number': work_data.get('nit_number', 'Unknown NIT'),
                    'estimated_cost': work_data.get('estimated_cost', 0),
                    'earnest_money': work_data.get('earnest_money', 0),
                    'time_completion': work_data.get('time_completion', 6),
                    'time_of_completion': work_data.get('time_completion', 6),  # Added for compatibility
                    'nit_date': work_data.get('nit_date', 'Not found'),
                    'receipt_date': work_data.get('receipt_date', 'Not found'),
                    'opening_date': work_data.get('opening_date', 'Not found'),
                    'date': work_data.get('nit_date', 'Not found')  # Added for compatibility
                }
                if work_data.get('works') and len(work_data['works']) > 0:
                    work_info.update({
                        'name': work_data['works'][0]['name'],
                        'item_no': work_data['works'][0]['item_no'],
                        'estimated_cost': work_data['works'][0]['estimated_cost'],
                        'earnest_money': work_data['works'][0]['earnest_money'],
                        'time_completion': work_data['works'][0]['time_completion'],
                        'time_of_completion': work_data['works'][0]['time_completion']  # Added for compatibility
                    })
                
                # Update current_work with work_info
                st.session_state.current_work['work_info'] = work_info
                
                report_generator = ReportGenerator()
                html_content = report_generator.generate_detailed_report(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                
                st.success("✅ Detailed report generated!")
                
                st.download_button(
                    label="📥 Download Detailed Report",
                    data=html_content,
                    file_name=f"detailed_report_{st.session_state.current_work['nit_number']}.html",
                    mime="text/html",
                    key="single_detailed"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating detailed report: {str(e)}")
                logging.error(f"Error generating detailed report: {e}")
def handle_document_generation():
    """Handle official document generation with individual options."""
    st.header("📝 Generate Individual Documents")
    
    if not st.session_state.current_work or not st.session_state.bidders:
        st.warning("⚠️ Please upload NIT document and add bidders first.")
        return
    
    st.info("💡 Tip: Use 'Generate Reports' section for bulk generation of all documents simultaneously!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generate Letter of Acceptance", type="secondary"):
            try:
                loa_gen = LetterAcceptanceGenerator()
                html_content = loa_gen.generate_letter_of_acceptance(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                
                st.success("✅ Letter of Acceptance generated!")
                
                st.download_button(
                    label="📥 Download Letter of Acceptance",
                    data=html_content,
                    file_name=f"letter_of_acceptance_{st.session_state.current_work['nit_number']}.html",
                    mime="text/html",
                    key="individual_loa"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating Letter of Acceptance: {str(e)}")
                logging.error(f"Error generating LOA: {e}")
    
    with col2:
        if st.button("📋 Generate Work Order", type="secondary"):
            try:
                wo_gen = WorkOrderGenerator()
                html_content = wo_gen.generate_work_order(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                
                st.success("✅ Work Order generated!")
                
                st.download_button(
                    label="📥 Download Work Order",
                    data=html_content,
                    file_name=f"work_order_{st.session_state.current_work['nit_number']}.html",
                    mime="text/html",
                    key="individual_wo"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating Work Order: {str(e)}")
                logging.error(f"Error generating work order: {e}")
    
    with col3:
        if st.button("🔍 Generate Scrutiny Sheet", type="secondary"):
            try:
                ss_gen = ScrutinySheetGenerator()
                html_content = ss_gen.generate_scrutiny_sheet(
                    st.session_state.current_work,
                    st.session_state.bidders
                )
                
                st.success("✅ Scrutiny Sheet generated!")
                
                st.download_button(
                    label="📥 Download Scrutiny Sheet",
                    data=html_content,
                    file_name=f"scrutiny_sheet_{st.session_state.current_work['nit_number']}.html",
                    mime="text/html",
                    key="individual_scrutiny"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating Scrutiny Sheet: {str(e)}")
                logging.error(f"Error generating scrutiny sheet: {e}")
    
    # Enhanced ZIP download section
    st.markdown("---")
    st.header("📦 Enhanced PDF & ZIP Download")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 LaTeX-Based PDF Generation")
        if st.button("📋 Generate All PDFs (LaTeX)", type="primary"):
            try:
                latex_gen = LatexPDFGenerator()
                documents = {}
                
                with st.spinner("Generating PDF documents..."):
                    # Generate all documents as PDFs
                    temp_dir = tempfile.mkdtemp()
                    
                    # Comparative Statement
                    comp_path = os.path.join(temp_dir, "comparative_statement.pdf")
                    if latex_gen.generate_comparative_statement_pdf(st.session_state.current_work, st.session_state.bidders, comp_path):
                        with open(comp_path, 'rb') as f:
                            documents['comparative_statement'] = f.read()
                    
                    # Letter of Acceptance
                    l1_bidder = min(st.session_state.bidders, key=lambda x: x.get('bid_amount', float('inf')))
                    loa_path = os.path.join(temp_dir, "letter_acceptance.pdf")
                    if latex_gen.generate_letter_acceptance_pdf(st.session_state.current_work, l1_bidder, loa_path):
                        with open(loa_path, 'rb') as f:
                            documents['letter_acceptance'] = f.read()
                    
                    # Work Order
                    wo_path = os.path.join(temp_dir, "work_order.pdf")
                    if latex_gen.generate_work_order_pdf(st.session_state.current_work, l1_bidder, wo_path):
                        with open(wo_path, 'rb') as f:
                            documents['work_order'] = f.read()
                    
                    # Scrutiny Sheet
                    ss_path = os.path.join(temp_dir, "scrutiny_sheet.pdf")
                    if latex_gen.generate_scrutiny_sheet_pdf(st.session_state.current_work, st.session_state.bidders, ss_path):
                        with open(ss_path, 'rb') as f:
                            documents['scrutiny_sheet'] = f.read()
                
                if documents:
                    st.success(f"✅ Generated {len(documents)} PDF documents!")
                    
                    # Store in session state for download
                    st.session_state.generated_pdfs = documents
                    
                    # Show individual download buttons
                    for doc_type, pdf_data in documents.items():
                        doc_name = doc_type.replace('_', ' ').title()
                        st.download_button(
                            label=f"📥 Download {doc_name} PDF",
                            data=pdf_data,
                            file_name=f"{doc_type}_{st.session_state.current_work['nit_number']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{doc_type}"
                        )
                else:
                    st.error("❌ Failed to generate PDF documents. Please check your data.")
                    
            except Exception as e:
                st.error(f"❌ Error generating PDF documents: {str(e)}")
                logging.error(f"Error generating PDFs: {e}")
    
    with col2:
        st.subheader("📦 One-Click ZIP Download")
        if st.button("🚀 Download All as ZIP", type="primary"):
            try:
                with st.spinner("Creating ZIP package..."):
                    zip_gen = ZipGenerator()
                    
                    # Check if we have generated PDFs
                    if hasattr(st.session_state, 'generated_pdfs') and st.session_state.generated_pdfs:
                        documents = st.session_state.generated_pdfs
                    else:
                        # Generate new PDFs if not available
                        documents = {}
                        latex_gen = LatexPDFGenerator()
                        temp_dir = tempfile.mkdtemp()
                        
                        # Generate all documents
                        comp_path = os.path.join(temp_dir, "comparative_statement.pdf")
                        if latex_gen.generate_comparative_statement_pdf(st.session_state.current_work, st.session_state.bidders, comp_path):
                            with open(comp_path, 'rb') as f:
                                documents['comparative_statement'] = f.read()
                        
                        if st.session_state.bidders:
                            l1_bidder = min(st.session_state.bidders, key=lambda x: x.get('bid_amount', float('inf')))
                            
                            loa_path = os.path.join(temp_dir, "letter_acceptance.pdf")
                            if latex_gen.generate_letter_acceptance_pdf(st.session_state.current_work, l1_bidder, loa_path):
                                with open(loa_path, 'rb') as f:
                                    documents['letter_acceptance'] = f.read()
                            
                            wo_path = os.path.join(temp_dir, "work_order.pdf")
                            if latex_gen.generate_work_order_pdf(st.session_state.current_work, l1_bidder, wo_path):
                                with open(wo_path, 'rb') as f:
                                    documents['work_order'] = f.read()
                        
                        ss_path = os.path.join(temp_dir, "scrutiny_sheet.pdf")
                        if latex_gen.generate_scrutiny_sheet_pdf(st.session_state.current_work, st.session_state.bidders, ss_path):
                            with open(ss_path, 'rb') as f:
                                documents['scrutiny_sheet'] = f.read()
                    
                    if documents:
                        # Create ZIP file
                        zip_data = zip_gen.create_tender_documents_zip(
                            st.session_state.current_work.get('work_name', 'Unknown_Work'),
                            st.session_state.current_work.get('nit_number', 'Unknown_NIT'),
                            documents
                        )
                        
                        if zip_data:
                            st.success(f"✅ ZIP package created with {len(documents)} documents!")
                            
                            # Create download button for ZIP
                            nit_number = st.session_state.current_work.get('nit_number', 'Unknown').replace('/', '_')
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            
                            st.download_button(
                                label="📦 Download Complete Package (ZIP)",
                                data=zip_data,
                                file_name=f"Tender_Documents_{nit_number}_{timestamp}.zip",
                                mime="application/zip",
                                type="primary"
                            )
                            
                            show_balloons()
                        else:
                            st.error("❌ Failed to create ZIP package.")
                    else:
                        st.error("❌ No documents available to package.")
                        
            except Exception as e:
                st.error(f"❌ Error creating ZIP package: {str(e)}")
                logging.error(f"Error creating ZIP: {e}")
        
        st.info("💡 The ZIP package includes:\n- All tender documents as PDFs\n- Summary file\n- Data reference file")



if __name__ == "__main__":
    main()
