# test_latex_pdf.py
import os
import streamlit as st
from latex_pdf_generator import LatexPDFGenerator

st.title("LatexPDFGenerator smoke test")

generator = LatexPDFGenerator()
st.write("✅ Class imported successfully")
st.write("Template dir exists:", os.path.isdir(generator.templates_dir))