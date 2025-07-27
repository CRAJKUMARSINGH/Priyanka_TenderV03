import streamlit as st
from comparative_statement_generator import ComparativeStatementGenerator

st.title("ComparativeStatementGenerator smoke-test")

gen = ComparativeStatementGenerator()

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
    {"name": "XYZ Co",  "percentage": 2.0,  "bid_amount": 1_020_000},
]

html = gen.generate_comparative_statement(work, bidders)

st.download_button(
    label="Download comparative.html",
    data=html.encode("utf-8"),
    file_name="comparative.html",
    mime="text/html"
)