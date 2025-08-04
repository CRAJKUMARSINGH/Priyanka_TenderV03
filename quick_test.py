# quick_test.py  (run as streamlit run quick_test.py)
import streamlit as st
from zip_generator import ZipGenerator

st.title("ZipGenerator smoke test")

dummy = {"hello.txt": b"hello world"}
zg = ZipGenerator()
zip_bytes = zg.create_zip(dummy)

if zip_bytes:
    st.success("ZipGenerator returned {} bytes".format(len(zip_bytes)))
    st.download_button("Download test.zip", zip_bytes, "test.zip")
else:
    st.error("ZipGenerator failed")
