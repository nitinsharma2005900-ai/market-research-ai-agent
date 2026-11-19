"""Streamlit Web Dashboard for Multi-Agent Market Research & Report Generator.

Provides an interactive GUI to execute the CrewAI hierarchical team, inspect
real-time agent routing, explore Pandas financial analytics, and download/preview
the compiled ReportLab A4 PDF report.
"""

import base64
import json
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from config.settings import (
    DATA_DIR,
    OUTPUT_DIR,
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
from crew.tools.financial_parser import (
    get_summary_dataframe,
    get_raw_dataframe,
    calculate_financial_metrics,
)
from crew.tools.scraper_tool import web_scraper_tool
from utils.benchmark import BenchmarkTracker
from utils.pdf_generator import generate_pdf_report
from main import run_live_crew_workflow, run_simulated_hierarchical_workflow

# Page Configuration
st.set_page_config(
    page_title="Market Research AI Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .agent-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #DBEAFE;
        color: #1E40AF;
        margin-right: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
st.sidebar.title("Configuration")

# Target Query
query_input = st.sidebar.text_input(
    "Market Research Query",
    value="Tech Sector Q3 Analysis",
    help="Enter the market sector or corporate topic to investigate.",
)

# Model Selection
model_choice = st.sidebar.selectbox(
    "Manager & Agent LLM (Gemini)",
    options=[
        "gemini/gemini-2.5-flash",
        "gemini/gemini-1.5-flash",
        "gemini/gemini-1.5-pro",
    ],
    index=0,
)

# API Key Config
env_key = os.getenv("GEMINI_API_KEY") or ""
api_key_input = st.sidebar.text_input(
    "Google Gemini API Key",
    value=env_key if not env_key.startswith("your_") else "",
    type="password",
    help="Leave blank to use resilient simulation mode with real tools.",
)

# Dataset Choice
st.sidebar.subheader("Dataset Settings")
data_source = st.sidebar.radio(
    "Financial Data Source",
    options=["Default Sample Dataset (Tech Equities)", "Upload Custom CSV"],
)

csv_path = DATA_DIR / "sample_financials.csv"
if data_source == "Upload Custom CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        custom_csv = DATA_DIR / uploaded_file.name
        with open(custom_csv, "wb") as f:
            f.write(uploaded_file.getbuffer())
        csv_path = custom_csv

# Execution Trigger
run_btn = st.sidebar.button("🚀 Run Multi-Agent Crew", type="primary", use_container_width=True)

# Main Banner
st.markdown('<div class="main-header">📊 Multi-Agent Market Research & Report Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Hierarchical CrewAI Team Orchestration powered by <b>Google Gemini</b>, <b>Pandas</b>, and <b>ReportLab</b>.</div>',
    unsafe_allow_html=True,
)

# Quick Badges
st.markdown(
    """
    <span class="agent-pill">Manager: Google Gemini</span>
    <span class="agent-pill">Architecture: Process.hierarchical</span>
    <span class="agent-pill">Researcher: Web Scraper Tool</span>
    <span class="agent-pill">Analyst: Pandas Describe Engine</span>
    <span class="agent-pill">Writer: ReportLab A4 PDF</span>
    """,
    unsafe_allow_html=True,
)
st.divider()

# Ensure Output Paths
output_pdf_path = OUTPUT_DIR / "market_report.pdf"
output_md_path = OUTPUT_DIR / "market_report.md"
benchmarks_json_path = OUTPUT_DIR / "benchmarks.json"

# Execution Logic
if run_btn:
    st.info(f"Initiating Hierarchical Workflow for: **{query_input}**...")
    tracker = BenchmarkTracker(output_path=str(benchmarks_json_path))
    tracker.start_workflow(query=query_input, model=model_choice)

    active_key = api_key_input.strip() or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    with st.spinner("Hierarchical Manager delegating tasks across Researcher, Analyst, and Writer..."):
        report_markdown = ""
        if active_key and not active_key.startswith("your_"):
            try:
                os.environ["GEMINI_API_KEY"] = active_key
                os.environ["GOOGLE_API_KEY"] = active_key
                report_markdown = run_live_crew_workflow(
                    query=query_input,
                    csv_path=str(csv_path),
                    model=model_choice,
                    tracker=tracker,
                )
            except Exception as exc:
                st.warning(f"Live Crew API call warning: {exc}. Engaging offline tool execution pipeline.")
                report_markdown = run_simulated_hierarchical_workflow(
                    query=query_input,
                    csv_path=str(csv_path),
                    tracker=tracker,
                )
        else:
            report_markdown = run_simulated_hierarchical_workflow(
                query=query_input,
                csv_path=str(csv_path),
                tracker=tracker,
            )

        # Write outputs
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(report_markdown)

        generate_pdf_report(
            markdown_content=report_markdown,
            output_pdf_path=str(output_pdf_path),
            query=query_input,
            csv_path=str(csv_path),
        )

        tracker.finish_workflow(success=True)

    st.success("Workflow completed successfully! PDF Report and Benchmarks generated.")

# Tabs for Content Navigation
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Executive Report & PDF",
    "📈 Quantitative Financial Analytics (Pandas)",
    "🤖 Agent Orchestration & Routing Trace",
    "⏱️ Performance Benchmarks",
])

# Tab 1: Executive Report & PDF
with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Executive Markdown Dossier")
        if output_md_path.is_file():
            with open(output_md_path, "r", encoding="utf-8") as f:
                md_text = f.read()
            st.markdown(md_text)
        else:
            st.info("No report generated yet. Click 'Run Multi-Agent Crew' to compile.")

    with col2:
        st.subheader("Compiled A4 PDF Report (ReportLab)")
        if output_pdf_path.is_file():
            with open(output_pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="📥 Download Executive PDF (market_report.pdf)",
                data=pdf_bytes,
                file_name="market_report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )

            # Display PDF iframe
            base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="750" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.info("No PDF compiled yet.")

# Tab 2: Quantitative Financial Analytics
with tab2:
    st.subheader("Financial Metrics & Statistical Summary")
    if csv_path.is_file():
        raw_df = get_raw_dataframe(str(csv_path))
        summary_df = get_summary_dataframe(str(csv_path))

        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("**Descriptive Statistics Matrix (Pandas Engine)**")
            st.dataframe(summary_df, use_container_width=True)

        with c2:
            st.markdown("**Raw Corporate Dataset**")
            st.dataframe(raw_df, use_container_width=True)

        st.subheader("Comparative Visualizations")
        chart_col1, chart_col2 = st.columns(2)
        if "Company" in raw_df.columns and "Revenue_B" in raw_df.columns:
            with chart_col1:
                st.bar_chart(data=raw_df.set_index("Company")["Revenue_B"], use_container_width=True)
                st.caption("Revenue ($B) by Company")

        if "Company" in raw_df.columns and "Net_Margin_Pct" in raw_df.columns:
            with chart_col2:
                st.bar_chart(data=raw_df.set_index("Company")["Net_Margin_Pct"], use_container_width=True)
                st.caption("Net Margin (%) by Company")

# Tab 3: Agent Orchestration & Routing Trace
with tab3:
    st.subheader("CrewAI Hierarchical Agent Team")

    ag1, ag2, ag3 = st.columns(3)
    with ag1:
        st.markdown(
            """
            <div class="metric-card">
                <h4>🔍 Lead Researcher</h4>
                <p><b>Role:</b> Market Research Specialist</p>
                <p><b>Goal:</b> Scrape search networks, discover corporate filings, gather macro data.</p>
                <p><b>Tools:</b> <code>web_scraper_tool</code>, <code>scrape_webpage_content</code></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with ag2:
        st.markdown(
            """
            <div class="metric-card">
                <h4>📊 Data Analyst</h4>
                <p><b>Role:</b> Financial Data Analyst</p>
                <p><b>Goal:</b> Parse data matrices using Pandas, compute averages, verify consistency.</p>
                <p><b>Tools:</b> <code>calculate_financial_metrics</code></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with ag3:
        st.markdown(
            """
            <div class="metric-card">
                <h4>✍️ Content Writer</h4>
                <p><b>Role:</b> Technical Reports Writer</p>
                <p><b>Goal:</b> Synthesize information, write sections, structure executive dossier.</p>
                <p><b>Output:</b> Publication-grade Markdown & ReportLab A4 PDF</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Dynamic Task Routing History")
    if benchmarks_json_path.is_file():
        with open(benchmarks_json_path, "r", encoding="utf-8") as f:
            b_data = json.load(f)

        routing_history = b_data.get("task_routing_history", [])
        for step in routing_history:
            st.markdown(f"- `{step}`")
    else:
        st.info("Run a workflow to inspect the routing history.")

# Tab 4: Performance Benchmarks
with tab4:
    st.subheader("Execution Benchmarking & Analytics")
    if benchmarks_json_path.is_file():
        with open(benchmarks_json_path, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Status", bench_data.get("status", "N/A"))
        m2.metric("Total Latency", f"{bench_data.get('total_execution_time_seconds', 0)}s")
        m3.metric("Tasks Completed", bench_data.get("summary", {}).get("total_tasks", 0))
        m4.metric("Avg Task Latency", f"{bench_data.get('summary', {}).get('average_task_latency_seconds', 0)}s")

        st.markdown("**Per-Task Execution Times:**")
        tasks_list = bench_data.get("task_benchmarks", [])
        if tasks_list:
            task_df = pd.DataFrame(tasks_list)[["task_name", "agent_role", "duration_seconds", "status"]]
            st.dataframe(task_df, use_container_width=True)

        st.markdown("**Raw JSON Metrics (`benchmarks.json`):**")
        st.json(bench_data)
    else:
        st.info("Run a workflow to generate performance benchmarks.")
