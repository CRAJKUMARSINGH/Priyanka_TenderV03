import streamlit as st
from document_generator import DocumentGenerator

st.title("DocumentGenerator smoke-test")

gen = DocumentGenerator()

# Minimal dummy data
work = {
    "work_name": "Demo Work",
    "nit_number": "123/25",
    "work_info": {
        "estimated_cost": 1_000_000,
        "earnest_money": 20_000,
        "time_of_completion": "3 Months",
        "date": "27-07-2025"
    }
}
bidders = [
    {"name": "ABC Ltd", "percentage": -5.5, "bid_amount": 945_000},
]

doc_bytes = gen.generate_comparative_statement_doc(work, bidders)

st.download_button(
    label="Download comparative.docx",
    data=doc_bytes,
    file_name="comparative.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)