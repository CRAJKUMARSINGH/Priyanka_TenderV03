import streamlit as st
from work_order_generator import WorkOrderGenerator

st.title("WorkOrderGenerator smoke-test")

gen = WorkOrderGenerator()

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
    {"name": "ABC Ltd", "percentage": -5.5, "bid_amount": 945_000}
]

html = gen.generate_work_order(work, bidders)

st.download_button(
    label="Download work_order.html",
    data=html.encode("utf-8"),
    file_name="work_order.html",
    mime="text/html"
)