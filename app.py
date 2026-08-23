import streamlit as st
import pandas as pd
import json
from src.ingestion.loader import load_data
from src.preprocessing import cleaner, report as dq_report
from src.database.report_store import save_report, list_reports, load_report

st.set_page_config(page_title="Automated Data Watchdog", layout="wide")

# Minimal monochrome styling
st.markdown(
    """
    <style>
    /* Reduce color usage for a minimal monochrome theme */
    .stApp { background-color: #ffffff; color: #111111; }
    .css-18e3th9 { background-color: #ffffff; }
    .stButton>button { background-color: #f2f2f2; color: #111111; }
    .stSidebar { background-color: #ffffff; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Automated Data Watchdog — Prototype")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Upload & Clean", "Saved Reports"])

if page == "Upload & Clean":
    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload a CSV/XLSX file", type=["csv","xls","xlsx"]) 

    # Preserve original and cleaned DataFrames in session state for undo/redo
    if 'original_df' not in st.session_state:
        st.session_state['original_df'] = None
    if 'cleaned_df' not in st.session_state:
        st.session_state['cleaned_df'] = None
    if 'last_report' not in st.session_state:
        st.session_state['last_report'] = None

    def _load_and_store(f):
        df, meta = load_data(f)
        st.session_state['original_df'] = df
        st.session_state['cleaned_df'] = None
        st.session_state['last_report'] = None
        return df, meta

    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None

    if uploaded_file is not None:
        df, meta = _load_and_store(uploaded_file)
        st.session_state['uploaded_file'] = uploaded_file
        st.sidebar.success("Loaded: {} rows, {} columns".format(df.shape[0], df.shape[1]))

        st.header("Data Preview")
        st.dataframe(df.head(200))

        # Data quality controls
        st.sidebar.header("Data Quality & Cleaning")
        drop_empty = st.sidebar.checkbox("Drop fully empty columns", value=True)
        drop_dups = st.sidebar.checkbox("Drop duplicate rows", value=True)
        btn_preview = st.sidebar.button("Preview Cleaning")
        btn_apply = st.sidebar.button("Apply Cleaning")
        btn_undo = st.sidebar.button("Undo Cleaning")

        if btn_preview:
            cleaned, log, report = cleaner.clean_data(df.copy(), drop_empty_cols=drop_empty, drop_duplicates=drop_dups)
            st.session_state['last_report'] = report
            st.subheader("Data Quality Report (Preview)")
            st.code(dq_report.generate_data_quality_report(report))
            st.subheader("Transformation Log")
            for row in log:
                st.write("- ", row)

            st.subheader("Cleaned Data Preview")
            st.dataframe(cleaned.head(200))

        if btn_apply:
            cleaned, log, report = cleaner.clean_data(df.copy(), drop_empty_cols=drop_empty, drop_duplicates=drop_dups)
            st.session_state['cleaned_df'] = cleaned
            st.session_state['last_report'] = report
            # persist report to DB
            try:
                save_report(report, source='upload', filename=getattr(uploaded_file, 'name', None))
                st.success("Cleaning applied and report saved to local DB")
            except Exception as e:
                st.error(f"Cleaning applied but failed to save report: {e}")

            st.subheader("Data Quality Report (Applied)")
            st.code(dq_report.generate_data_quality_report(report))

            st.subheader("Transformation Log")
            for row in log:
                st.write("- ", row)

            st.subheader("Cleaned Data Preview")
            st.dataframe(cleaned.head(200))

        if btn_undo:
            if st.session_state['original_df'] is not None:
                st.session_state['cleaned_df'] = None
                st.session_state['last_report'] = None
                st.success("Reverted to original uploaded dataset")
            else:
                st.info("No dataset to revert to")

        # Show latest saved report (if present)
        if st.session_state.get('last_report') is not None and not btn_preview and not btn_apply:
            st.subheader("Last Computed Data Quality Report")
            st.markdown(dq_report.report_to_markdown(st.session_state['last_report']))

    else:
        st.info("No file uploaded. A small sample dataset is included at data/sample/sample_business_data.csv — run app locally or upload your own file.")

elif page == "Saved Reports":
    st.header("Saved Data Quality Reports")
    try:
        rows = list_reports(100)
    except Exception as e:
        st.error(f"Failed to load saved reports: {e}")
        rows = []

    if rows:
        df_meta = pd.DataFrame(rows)
        st.dataframe(df_meta)

        options = [f"{r['id']} | {r['created_at']} | {r.get('filename')}" for r in rows]
        sel = st.selectbox("Select report to view", options)
        if sel:
            rid = int(sel.split('|')[0].strip())
            loaded = load_report(rid)
            if loaded:
                st.subheader(f"Report {loaded['id']} — {loaded['created_at']}")
                st.markdown(dq_report.report_to_markdown(loaded['report']))
                st.subheader("Raw JSON")
                st.code(json.dumps(loaded['report'], indent=2))
                st.download_button("Download JSON", data=json.dumps(loaded['report'], indent=2), file_name=f"report_{loaded['id']}.json", mime="application/json")
            else:
                st.error("Could not load selected report")
    else:
        st.info("No saved reports found")
