import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Workforce Productivity Command Center", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("📊 Workforce Analytics")
uploaded_file = st.sidebar.file_uploader("Update Data (XLSX)", type=["xlsx"])

if uploaded_file:
    # STEP 1: LOAD DATA
    df = pd.read_excel(uploaded_file)
    
    # STEP 2: CLEAN HEADERS AND DATES
    if df.iloc[0,0] == "Row Labels":
        df = df.iloc[1:].reset_index(drop=True)

    df['Date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce', dayfirst=True).dt.date
    df = df.dropna(subset=['Date'])

    # --- THE FIX: CLEAN THE FILTER OPTIONS ---
    # Strip out 'NaN' (empty cells) before making the dropdown lists
    sub_options = df.iloc[:, 3].dropna().unique().tolist()
    trade_options = df.iloc[:, 2].dropna().unique().tolist()

    subcontractors = st.sidebar.multiselect("Subcontractor", options=sub_options, default=sub_options)
    trades = st.sidebar.multiselect("Trade", options=trade_options, default=trade_options)

    # Filtering Data based on selections
    df_filtered = df[(df.iloc[:, 3].isin(subcontractors)) & (df.iloc[:, 2].isin(trades))]

    # KPI Header
    st.title("Workforce Productivity Command Center")
    
    # KPI Calculations (with safety checks in case data is completely filtered out)
    total_workers = df_filtered.iloc[:, 1].nunique() if not df_filtered.empty else 0
    total_idle_hrs = df_filtered.iloc[:, 5].sum() if not df_filtered.empty else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTAL WORKERS", total_workers)
    c2.metric("TOTAL IDLE HOURS", f"{total_idle_hrs:.1f}h")
    c3.metric("FINANCIAL LOSS", f"₹{total_idle_hrs * 250:,.0f}")

    # Charts
    if not df_filtered.empty:
        col_left, col_right = st.columns(2)
        
        with col_left:
            daily_trend = df_filtered.groupby('Date').size().reset_index(name='Flags')
            fig_line = px.line(daily_trend, x='Date', y='Flags', title="Daily Flagged Trends")
            st.plotly_chart(fig_line, use_container_width=True)

        with col_right:
            sub_pie = px.pie(df_filtered, names=df_filtered.columns[3], title="Loss by Subcontractor", hole=0.4)
            st.plotly_chart(sub_pie, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

else:
    st.warning("Waiting for Excel upload...")
