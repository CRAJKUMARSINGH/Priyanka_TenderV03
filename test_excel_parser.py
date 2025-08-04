import streamlit as st
from excel_parser import ExcelParser
import tempfile

st.title("ExcelParser smoke-test")

parser = ExcelParser()

uploaded = st.file_uploader("Upload NIT Excel file", type=['xlsx', 'xls'])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(uploaded.getbuffer())
        tmp.flush()

        data = parser.parse_nit_excel(tmp.name)
        if data:
            st.success("✅ Parsed successfully")
            st.json(data)
        else:
            st.error("❌ Could not parse file")
