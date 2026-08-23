import streamlit as st
import pandas as pd
from src.ingestion.loader import load_data

st.set_page_config(page_title="Automated Data Watchdog", layout="wide")

st.title("Automated Data Watchdog — Prototype")

st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV/XLSX file", type=["csv","xls","xlsx"]) 

if uploaded_file is not None:
    df, meta = load_data(uploaded_file)
    st.sidebar.success("Loaded: {} rows, {} columns".format(df.shape[0], df.shape[1]))

    st.header("Data Preview")
    st.dataframe(df.head(200))

    st.header("Detected Columns")
    st.write(meta)
else:
    st.info("No file uploaded. A small sample dataset is included at data/sample/sample_business_data.csv — run app locally or upload your own file.")

