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
    
    # STEP 2: FIX THE "ROW LABELS" ERROR
    # If the first row contains "Row Labels", we skip it or clean it
    if df.iloc[0,0] == "Row Labels":
        df = df.iloc[1:].reset_index(drop=True)

    # STEP 3: CONVERT DATE SAFELY
    # dayfirst=True is used for Indian/International date formats (DD-MM-YYYY)
    df['Date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce', dayfirst=True).dt.date
    
    # Remove any rows where the date couldn't be parsed (empty rows)
    df = df.dropna(subset=['Date'])

    # --- THE REST OF YOUR DASHBOARD LOGIC ---
    # Sidebar Filters
    subcontractors = st.sidebar.multiselect("Subcontractor", options=df.iloc[:, 3].unique(), default=df.iloc[:, 3].unique())
    trades = st.sidebar.multiselect("Trade", options=df.iloc[:, 2].unique(), default=df.iloc[:, 2].unique())

    # Filtering Data
    df_filtered = df[(df.iloc[:, 3].isin(subcontractors)) & (df.iloc[:, 2].isin(trades))]

    # KPI Header
    st.title("Workforce Productivity Command Center")
    
    # KPI Calculations
    total_workers = df_filtered.iloc[:, 1].nunique()
    total_idle_hrs = df_filtered.iloc[:, 5].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTAL WORKERS", total_workers)
    c2.metric("TOTAL IDLE HOURS", f"{total_idle_hrs:.1f}h")
    c3.metric("FINANCIAL LOSS", f"₹{total_idle_hrs * 250:,.0f}")

    # Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        daily_trend = df_filtered.groupby('Date').size().reset_index(name='Flags')
        fig_line = px.line(daily_trend, x='Date', y='Flags', title="Daily Flagged Trends")
        st.plotly_chart(fig_line, use_container_width=True)

    with col_right:
        sub_pie = px.pie(df_filtered, names=df_filtered.columns[3], title="Loss by Subcontractor", hole=0.4)
        st.plotly_chart(sub_pie, use_container_width=True)

else:
    st.warning("Waiting for Excel upload...")
