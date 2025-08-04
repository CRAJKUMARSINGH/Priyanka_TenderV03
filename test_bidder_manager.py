import streamlit as st
from bidder_manager import BidderManager

st.title("BidderManager smoke-test")

bm = BidderManager(":memory:")  # in-memory file for test

# Add a dummy bidder
bm.add_bidder({
    "name": "ABC Ltd",
    "percentage": -5.5,
    "bid_amount": 945_000
})

bidders = bm.get_all_bidders()

st.write("✅ Total bidders:", len(bidders))
st.json(bidders)
