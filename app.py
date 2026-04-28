import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Workforce Productivity Command Center", layout="wide")

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR / FILTERS ---
st.sidebar.title("📊 Workforce Analytics")
st.sidebar.caption("Construction site productivity intelligence")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("Update Data (XLSX)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Pre-processing: Clean up column names and convert types
    # Assuming columns: Date, Worker, Profession, Subcontractor, Zones, Idle Hours
    df['Date'] = pd.to_datetime(df.iloc[:, 0]).dt.date
    
    # Sidebar Filters
    date_range = st.sidebar.date_input("Date Range", [df['Date'].min(), df['Date'].max()])
    subcontractors = st.sidebar.multiselect("Subcontractor", options=df.iloc[:, 3].unique(), default=df.iloc[:, 3].unique())
    trades = st.sidebar.multiselect("Trade", options=df.iloc[:, 2].unique(), default=df.iloc[:, 2].unique())
    zones = st.sidebar.slider("Zones Visited", 1, int(df.iloc[:, 4].max()), (1, int(df.iloc[:, 4].max())))

    # Filtering Data
    mask = (df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1]) & \
           (df.iloc[:, 3].isin(subcontractors)) & (df.iloc[:, 2].isin(trades)) & \
           (df.iloc[:, 4].between(zones[0], zones[1]))
    df_filtered = df[mask]

    # --- MAIN DASHBOARD ---
    st.title("Workforce Productivity Command Center")
    st.caption("Live tracking of low-productivity workers across subcontractors, trades, and zones")

    # --- KPI CARDS ---
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_workers = df_filtered.iloc[:, 1].nunique()
    total_idle = df_filtered.iloc[:, 5].sum() # Assuming 6th col is Idle Hours
    avg_work = 8 - (total_idle / len(df_filtered)) # Simple logic: 8hr shift minus idle
    productivity = (avg_work / 8) * 100

    col1.metric("TOTAL WORKERS", f"{total_workers}")
    col2.metric("AVG WORK HOURS", f"{avg_work:.2f}h")
    col3.metric("TOTAL IDLE HOURS", f"{total_idle:.0f}h")
    col4.metric("FLAGGED ENTRIES", f"{len(df_filtered)}")
    col5.metric("PRODUCTIVITY %", f"{productivity:.1f}%")

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["Overview", "Workers", "Subcontractors"])

    with tab1:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            # Daily Trend
            daily_trend = df_filtered.groupby('Date').size().reset_index(name='Flags')
            fig_trend = px.line(daily_trend, x='Date', y='Flags', title="Daily Productivity Trend", markers=True)
            fig_trend.update_traces(line_color='#4e73df')
            st.plotly_chart(fig_trend, use_container_width=True)

        with c2:
            # Severity Donut (Mock logic based on Idle Hours)
            df_filtered['Severity'] = df_filtered.iloc[:, 5].apply(lambda x: 'Severe' if x > 4 else 'Mild')
            fig_donut = px.pie(df_filtered, names='Severity', hole=0.7, title="Severity Distribution",
                               color_discrete_map={'Severe':'#e74a3b', 'Mild':'#f6c23e'})
            st.plotly_chart(fig_donut, use_container_width=True)

        c3, c4 = st.columns([2, 1])
        
        with c3:
            # Stacked Bar
            fig_stack = px.bar(df_filtered, x='Date', color='Severity', title="Flagged Workers per Day",
                               color_discrete_map={'Severe':'#e74a3b', 'Mild':'#f6c23e'}, barmode='stack')
            st.plotly_chart(fig_stack, use_container_width=True)
            
        with c4:
            # Subcontractor Split
            fig_sub = px.pie(df_filtered, names=df_filtered.columns[3], hole=0.5, title="Workers by Subcontractor")
            st.plotly_chart(fig_sub, use_container_width=True)

else:
    st.info("Please upload your Excel file in the sidebar to generate the Command Center.")
