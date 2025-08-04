# test_direct.py  (run with:  streamlit run test_direct.py)
import streamlit as st
from excel_parser import ExcelParser
import os

st.title("Direct parser test")

# Change this to your actual file
file_path = "test_files/sample_nit.xlsx"   # put your real file in repo

if os.path.exists(file_path):
    parser = ExcelParser()
    data = parser.parse_nit_excel(file_path)

    if data:
        st.success("Parsed!")
        st.json(data)
    else:
        st.error("Parser returned None")
else:
    st.warning("Place your Excel in ./test_files/sample_nit.xlsx")
