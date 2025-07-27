import streamlit as st
from tender_processor import TenderProcessor

st.title("TenderProcessor smoke-test")

proc = TenderProcessor()

# Minimal dummy data
work = {
    "work_name": "Demo Work",
    "nit_number": "123/25",
    "work_info": {
        "estimated_cost": 1_000_000,
        "date": "27-07-2025",
        "time_of_completion": "3 Months"
    }
}
bidders = [
    {"name": "A", "percentage": -5.5, "bid_amount": 945_000},
    {"name": "B", "percentage": 2.0, "bid_amount": 1_020_000},
]

# Test core methods
work_valid = proc.validate_work_data(work)
bidders_ranked = proc.rank_bidders(bidders)
stats = proc.calculate_statistics(bidders_ranked)

st.write("✅ validate_work_data:", work_valid)
st.write("✅ rank_bidders:", bidders_ranked)
st.write("✅ stats:", stats)