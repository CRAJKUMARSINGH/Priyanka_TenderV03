# test_pdf_gen.py   (run with: streamlit run test_pdf_gen.py)
import streamlit as st
from pdf_generator import PDFGenerator

st.title("PDFGenerator smoke-test")

gen = PDFGenerator()

# Minimal dummy data
work = {
    "work_name": "Demo Work",
    "nit_number": "123/25",
    "work_info": {
        "estimated_cost": 1000000,
        "earnest_money": 20000,
        "time_of_completion": 6,
        "date": "2025-07-27"
    }
}
bidders = [
    {"name": "ABC Ltd", "percentage": -5.5, "bid_amount": 945000, "earnest_money": 20000}
]

pdf_bytes = gen.generate_comparative_statement_pdf(work, bidders)

st.success(f"PDF generated, {len(pdf_bytes)} bytes")
st.download_button("Download demo.pdf", pdf_bytes, "demo.pdf", mime="application/pdf")
