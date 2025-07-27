"""
Streamlit front-end for the tender extractor.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from main import process_folder   # reuse the CLI logic

st.set_page_config(page_title="Tender Extractor", page_icon="📄")

st.title("📄 Tender PDF Extractor")
st.write("Upload one or more tender PDFs and get an instant Excel summary.")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type="pdf",
    accept_multiple_files=True
)

if st.button("Process") and uploaded_files:
    with st.spinner("Processing..."):
        # Create temp dirs
        tmp_in  = Path("tmp_input")
        tmp_out = Path("tmp_output")
        tmp_in.mkdir(exist_ok=True)
        tmp_out.mkdir(exist_ok=True)

        # Save uploads
        for f in uploaded_files:
            (tmp_in / f.name).write_bytes(f.getbuffer())

        # Reuse CLI engine
        process_folder(str(tmp_in), str(tmp_out))

        # Show result
        excel_path = tmp_out / "Tender_Summary.xlsx"
        if excel_path.exists():
            df = pd.read_excel(excel_path)
            st.success("Done!")
            st.dataframe(df)

            with open(excel_path, "rb") as fp:
                st.download_button(
                    label="⬇️ Download Excel",
                    data=fp,
                    file_name="Tender_Summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("No output generated. Check logs.")
