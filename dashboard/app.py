import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Audit Dashboard | AI Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR ENTERPRISE LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid #4F81BD;
    }
    .status-valid { color: #28a745; font-weight: bold; }
    .status-partial { color: #ffc107; font-weight: bold; }
    .status-invalid { color: #dc3545; font-weight: bold; }
    .status-broken { color: #8b0000; font-weight: bold; }
    h1, h2, h3 { color: #2c3e50; }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_latest_report():
    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    if not reports_dir.exists():
        return None
    
    # Find latest JSON
    json_files = list(reports_dir.glob("audit_*.json"))
    if not json_files:
        return None
    
    latest_file = max(json_files, key=os.path.getctime)
    with open(latest_file, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data)

df = load_latest_report()

if df is None or df.empty:
    st.error("No audit reports found. Please run the AI verification agent first.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

institutes = ["All"] + sorted(df['institute_name'].unique().tolist())
selected_institute = st.sidebar.selectbox("Filter by Institute", institutes)

statuses = ["All"] + sorted(df['verification_status'].unique().tolist())
selected_status = st.sidebar.selectbox("Filter by Status", statuses)

# Apply filters
filtered_df = df.copy()
if selected_institute != "All":
    filtered_df = filtered_df[filtered_df['institute_name'] == selected_institute]
if selected_status != "All":
    filtered_df = filtered_df[filtered_df['verification_status'] == selected_status]

# --- KPI METRICS ---
st.title("🛡️ Data Integrity Audit Dashboard")
st.markdown("Enterprise-grade overview of dataset verification and anomalies.")

total_rows = len(filtered_df)
valid_rows = len(filtered_df[filtered_df['verification_status'] == 'VALID'])
broken_links = len(filtered_df[filtered_df['verification_status'] == 'BROKEN_LINK'])
avg_confidence = filtered_df['confidence_score'].mean() * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records Processed", f"{total_rows}")
col2.metric("Valid Entries", f"{valid_rows}", f"{(valid_rows/total_rows*100):.1f}%" if total_rows > 0 else "0%")
col3.metric("Broken Links", f"{broken_links}", delta_color="inverse")
col4.metric("Avg Confidence Score", f"{avg_confidence:.1f}%")

st.markdown("---")

# --- CHARTS ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Verification Status Distribution")
    status_counts = filtered_df['verification_status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    color_map = {
        'VALID': '#28a745', 'PARTIAL_MATCH': '#ffc107', 
        'INVALID': '#dc3545', 'BROKEN_LINK': '#8b0000'
    }
    fig1 = px.pie(status_counts, values='Count', names='Status', hole=0.4,
                 color='Status', color_discrete_map=color_map)
    st.plotly_chart(fig1, use_container_width=True)

with col_chart2:
    st.subheader("Confidence Score Distribution")
    fig2 = px.histogram(filtered_df, x="confidence_score", nbins=10,
                       color="verification_status", color_discrete_map=color_map,
                       labels={'confidence_score': 'Confidence Score'})
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- ROW DETAILS ---
st.subheader("Detailed Course Verifications")

for idx, row in filtered_df.iterrows():
    status_color = color_map.get(row['verification_status'], '#6c757d')
    with st.expander(f"[{row['verification_status']}] {row['institute_name']} - {row['course_name']}"):
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            st.markdown("### AI Summary")
            st.info(row['ai_summary'])
            
            st.markdown("### Specific Fields Verified")
            st.markdown(f"- **Institute Name**: {row.get('verified_institute_name', 'N/A')}")
            st.markdown(f"- **Course Mode**: {row.get('verified_mode', 'N/A')}")
            st.markdown(f"- **Country**: {row.get('verified_country', 'N/A')}")
            st.markdown(f"- **Skills / Description**: {row.get('verified_skills', 'N/A')}")
            
            if row.get('suggested_corrections'):
                st.markdown("### Suggested Corrections")
                st.json(row['suggested_corrections'])
                
        with col_b:
            st.markdown("### Metadata")
            st.markdown(f"**Confidence**: {row['confidence_score']*100:.1f}%")
            st.markdown(f"**Response Time**: {row.get('response_time_ms', 0)} ms")
            st.markdown(f"**Link Status**: {row['link_status']}")
            st.markdown(f"[🔗 View Course Link]({row['course_link']})")
            
            if row.get('screenshot_path'):
                st.warning("⚠️ Page Failed to Load")
                if os.path.exists(row['screenshot_path']):
                    st.image(row['screenshot_path'], caption="Error Screenshot")

