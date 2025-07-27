import streamlit as st
from scrutiny_sheet_generator import ScrutinySheetGenerator

st.title("ScrutinySheetGenerator smoke-test")

gen = ScrutinySheetGenerator()

# Minimal dummy data
work = {
    "work_name": "Demo Work",
    "nit_number": "123/25",
    "work_info": {
        "estimated_cost": 1000000,
        "date": "27-07-2025"
    }
}
bidders = [
    {"name": "ABC Ltd", "percentage": -5.5, "bid_amount": 945000}
]

html = gen.generate_scrutiny_sheet(work, bidders)

st.download_button(
    label="Download scrutiny.html",
    data=html.encode("utf-8"),
    file_name="scrutiny.html",
    mime="text/html"
)