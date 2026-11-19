"""Market Research AI - Enterprise SaaS Financial Intelligence Platform.

Modern, premium interface powered by:
- CrewAI Hierarchical Team Orchestration
- Google Gemini Supervisor LLM
- Pandas Quantitative Financial Analytics Engine
- ReportLab Publication-Grade A4 PDF Compiler
- Plotly Interactive Visualizations
"""

import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config.settings import (
    DATA_DIR,
    OUTPUT_DIR,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    TEMPERATURE,
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

# -----------------------------------------------------------------------------
# Streamlit Application Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Market Research AI | Financial Intelligence Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Premium FinTech SaaS Custom CSS Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Background and Layout */
    .stApp {
        background: radial-gradient(circle at top right, #0F172A 0%, #080C16 60%, #05070E 100%);
        color: #F8FAFC;
    }

    /* Ambient Glow Hero Banner */
    .hero-container {
        position: relative;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 38px 40px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        overflow: hidden;
    }

    .hero-container::before {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 260px;
        height: 260px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(6, 182, 212, 0) 70%);
        border-radius: 50%;
        filter: blur(40px);
        z-index: 0;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 20%, #93C5FD 70%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin-bottom: 8px;
        position: relative;
        z-index: 1;
    }

    .hero-tagline {
        font-size: 1.15rem;
        color: #94A3B8;
        font-weight: 400;
        margin-bottom: 20px;
        letter-spacing: -0.01em;
        position: relative;
        z-index: 1;
    }

    /* Badges */
    .tech-badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        position: relative;
        z-index: 1;
    }

    .tech-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 24px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(30, 41, 59, 0.85);
        color: #E2E8F0;
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: all 0.2s ease;
    }

    .tech-badge:hover {
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(49, 46, 129, 0.4);
        transform: translateY(-1px);
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.35);
        box-shadow: 0 16px 32px -8px rgba(99, 102, 241, 0.2);
    }

    /* Agent Activity Card */
    .agent-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.5) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .agent-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 28px -6px rgba(0, 0, 0, 0.5);
    }

    .agent-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    .agent-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0;
    }

    .agent-role {
        font-size: 0.78rem;
        font-weight: 600;
        color: #38BDF8;
        margin-bottom: 8px;
    }

    .agent-desc {
        font-size: 0.83rem;
        color: #94A3B8;
        line-height: 1.45;
        margin-bottom: 14px;
    }

    /* Pulsing status indicator */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
    }

    .status-ready {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .pulse-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #34D399;
        box-shadow: 0 0 8px #34D399;
        animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.3); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* KPI Stat Metric Cards */
    .kpi-metric-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        text-align: left;
        box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .kpi-metric-box:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }

    .kpi-metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #94A3B8;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }

    .kpi-metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.02em;
    }

    .kpi-metric-sub {
        font-size: 0.75rem;
        color: #38BDF8;
        font-weight: 500;
        margin-top: 4px;
    }

    /* Primary Gradient Button Override */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #06B6D4 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-size: 0.95rem !important;
        letter-spacing: -0.01em !important;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.45) !important;
        transition: all 0.25s ease !important;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 30px -5px rgba(6, 182, 212, 0.6) !important;
        filter: brightness(1.08) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #080C14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 18px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: #94A3B8 !important;
        border: none !important;
        background: transparent !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(6, 182, 212, 0.2) 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
    }

    /* Timeline step */
    .timeline-item {
        border-left: 2px solid #6366F1;
        padding-left: 14px;
        margin-bottom: 12px;
        position: relative;
    }
    .timeline-item::before {
        content: "";
        position: absolute;
        left: -6px;
        top: 4px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #38BDF8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Base Directories & Output Paths
# -----------------------------------------------------------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

output_pdf_path = OUTPUT_DIR / "market_report.pdf"
output_md_path = OUTPUT_DIR / "market_report.md"
benchmarks_json_path = OUTPUT_DIR / "benchmarks.json"
default_csv_path = DATA_DIR / "sample_financials.csv"

# -----------------------------------------------------------------------------
# Sidebar Navigation & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
            <div style="width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #6366F1, #06B6D4); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 800; color: #FFFFFF;">α</div>
            <div>
                <div style="font-weight: 800; font-size: 1.15rem; color: #FFFFFF; letter-spacing: -0.02em;">AlphaResearch</div>
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 500;">INSTITUTIONAL AI PLATFORM</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height: 1px; background: rgba(255,255,255,0.06); margin-bottom: 18px;"></div>', unsafe_allow_html=True)

    nav_choice = st.radio(
        "Navigation",
        options=[
            "🚀 Research Workspace",
            "📈 Financial Analytics",
            "🤖 Agent Swarm & Routing",
            "📑 Report Vault & PDF",
            "⚙️ Platform Settings",
        ],
        label_visibility="collapsed",
    )

    st.markdown('<div style="height: 1px; background: rgba(255,255,255,0.06); margin: 20px 0;"></div>', unsafe_allow_html=True)

    # Mini System Monitor Box
    st.markdown(
        f"""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 14px; font-size: 0.78rem;">
            <div style="color: #94A3B8; font-weight: 600; margin-bottom: 8px;">SYSTEM ORCHESTRATION</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748B;">Manager LLM:</span>
                <span style="color: #38BDF8; font-weight: 600;">{GEMINI_MODEL.split('/')[-1]}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748B;">Process:</span>
                <span style="color: #34D399; font-weight: 600;">Hierarchical</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #64748B;">Specialized Agents:</span>
                <span style="color: #F8FAFC; font-weight: 600;">3 Active</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Reusable Helper: Plotly Financial Charts
# -----------------------------------------------------------------------------
def create_financial_charts(df: pd.DataFrame):
    """Builds interactive Plotly charts with modern dark styling."""
    charts = {}

    # 1. Revenue Comparison Bar Chart
    if "Company" in df.columns and "Revenue_B" in df.columns:
        fig_rev = px.bar(
            df.sort_values(by="Revenue_B", ascending=True),
            x="Revenue_B",
            y="Company",
            orientation="h",
            text="Revenue_B",
            title="Quarterly Revenue Benchmark ($B)",
            color="Revenue_B",
            color_continuous_scale=["#6366F1", "#06B6D4", "#38BDF8"],
        )
        fig_rev.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20),
            coloraxis_showscale=False,
            height=320,
            font=dict(family="Plus Jakarta Sans", color="#94A3B8"),
            xaxis=dict(title="Revenue ($B)", gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(title=""),
        )
        fig_rev.update_traces(texttemplate="$%{text:.1f}B", textposition="outside")
        charts["revenue"] = fig_rev

    # 2. Operating Margin vs YoY Growth Quadrant
    if "Net_Margin_Pct" in df.columns and "YoY_Growth_Pct" in df.columns and "Company" in df.columns:
        fig_scatter = px.scatter(
            df,
            x="YoY_Growth_Pct",
            y="Net_Margin_Pct",
            text="Company",
            size="Revenue_B" if "Revenue_B" in df.columns else None,
            color="Net_Margin_Pct",
            color_continuous_scale=["#38BDF8", "#818CF8", "#C084FC"],
            title="Growth vs. Profitability Quadrant Matrix",
            labels={
                "YoY_Growth_Pct": "YoY Revenue Growth (%)",
                "Net_Margin_Pct": "Net Profit Margin (%)",
            },
        )
        fig_scatter.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20),
            coloraxis_showscale=False,
            height=320,
            font=dict(family="Plus Jakarta Sans", color="#94A3B8"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        )
        fig_scatter.update_traces(textposition="top center", marker=dict(size=14, line=dict(width=1, color="#FFFFFF")))
        charts["scatter"] = fig_scatter

    # 3. P/E Multiple Benchmark
    if "Company" in df.columns and "PE_Ratio" in df.columns:
        fig_pe = px.bar(
            df.sort_values(by="PE_Ratio", ascending=False),
            x="Company",
            y="PE_Ratio",
            title="Price-to-Earnings (P/E) Multiple Valuation",
            color="PE_Ratio",
            color_continuous_scale=["#0EA5E9", "#6366F1", "#A855F7"],
            text="PE_Ratio",
        )
        fig_pe.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20),
            coloraxis_showscale=False,
            height=300,
            font=dict(family="Plus Jakarta Sans", color="#94A3B8"),
            xaxis=dict(title="", tickangle=-30),
            yaxis=dict(title="P/E Multiple (x)", gridcolor="rgba(255,255,255,0.06)"),
        )
        fig_pe.update_traces(texttemplate="%{text:.1f}x", textposition="outside")
        charts["pe"] = fig_pe

    # 4. Cash Flow vs R&D Capital Allocation
    if "Company" in df.columns and "Free_Cash_Flow_B" in df.columns and "RD_Expense_B" in df.columns:
        fig_cap = go.Figure()
        fig_cap.add_trace(go.Bar(
            name="Free Cash Flow ($B)",
            x=df["Company"],
            y=df["Free_Cash_Flow_B"],
            marker_color="#06B6D4",
        ))
        fig_cap.add_trace(go.Bar(
            name="R&D Expense ($B)",
            x=df["Company"],
            y=df["RD_Expense_B"],
            marker_color="#818CF8",
        ))
        fig_cap.update_layout(
            barmode="group",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title="Capital Allocation: Free Cash Flow vs. R&D Expense ($B)",
            margin=dict(l=20, r=20, t=40, b=20),
            height=300,
            font=dict(family="Plus Jakarta Sans", color="#94A3B8"),
            xaxis=dict(title="", tickangle=-30),
            yaxis=dict(title="$ Billion", gridcolor="rgba(255,255,255,0.06)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        charts["capital"] = fig_cap

    return charts

# =============================================================================
# VIEW 1: RESEARCH WORKSPACE (Landing Page & Generation Engine)
# =============================================================================
if nav_choice == "🚀 Research Workspace":
    # Hero Section
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">Market Research AI</div>
            <div class="hero-tagline">Autonomous Multi-Agent Financial Intelligence Platform. Intelligence That Drives Better Decisions.</div>
            <div class="tech-badge-container">
                <span class="tech-badge"><span>⚡</span> CrewAI 1.15 Hierarchical Engine</span>
                <span class="tech-badge"><span>🧠</span> Google Gemini 2.5 Flash</span>
                <span class="tech-badge"><span>📊</span> Pandas Matrix Analytics</span>
                <span class="tech-badge"><span>📑</span> ReportLab Typeset A4 PDF</span>
                <span class="tech-badge"><span>🌐</span> Live Web Crawling</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top KPI Metrics Strip (If CSV exists)
    if default_csv_path.is_file():
        raw_df = get_raw_dataframe(str(default_csv_path))
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
                <div class="kpi-metric-box">
                    <div class="kpi-metric-label">Universe Tracked</div>
                    <div class="kpi-metric-value">{len(raw_df)} Issuers</div>
                    <div class="kpi-metric-sub">Mega-Cap Tech Equities</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            median_rev = raw_df["Revenue_B"].median() if "Revenue_B" in raw_df.columns else 0.0
            st.markdown(
                f"""
                <div class="kpi-metric-box">
                    <div class="kpi-metric-label">Median Revenue</div>
                    <div class="kpi-metric-value">${median_rev:,.1f}B</div>
                    <div class="kpi-metric-sub">Quarterly Aggregate Base</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            avg_margin = raw_df["Net_Margin_Pct"].mean() if "Net_Margin_Pct" in raw_df.columns else 0.0
            st.markdown(
                f"""
                <div class="kpi-metric-box">
                    <div class="kpi-metric-label">Mean Net Margin</div>
                    <div class="kpi-metric-value">{avg_margin:.1f}%</div>
                    <div class="kpi-metric-sub">Weighted Operating Margin</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            median_pe = raw_df["PE_Ratio"].median() if "PE_Ratio" in raw_df.columns else 0.0
            st.markdown(
                f"""
                <div class="kpi-metric-box">
                    <div class="kpi-metric-label">Median P/E Multiple</div>
                    <div class="kpi-metric-value">{median_pe:.1f}x</div>
                    <div class="kpi-metric-sub">NTM Earnings Multiple</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)

    # Input Box & Query Selector
    st.markdown("### 🔍 Initiate Sector Intelligence Investigation")
    query_col, btn_col = st.columns([4, 1.2])

    with query_col:
        target_query = st.text_input(
            "Research Query Target",
            value="Tech Sector Q3 Analysis",
            placeholder="e.g. AI Semiconductor Infrastructure, Cloud Hyperscalers, EV Markets",
            label_visibility="collapsed",
        )

    with btn_col:
        run_trigger = st.button("🚀 Generate Report", type="primary", use_container_width=True)

    # Instant Sector Chips
    st.markdown(
        """
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: -6px; margin-bottom: 22px;">
            <span style="font-size: 0.76rem; color: #64748B; font-weight: 600; line-height: 24px;">SUGGESTED SECTORS:</span>
            <span class="tech-badge" style="cursor: pointer;">Tech Sector Q3 Analysis</span>
            <span class="tech-badge" style="cursor: pointer;">Generative AI Hardware & Compute</span>
            <span class="tech-badge" style="cursor: pointer;">Hyperscale Cloud & SaaS Multiples</span>
            <span class="tech-badge" style="cursor: pointer;">Electric Vehicle Autonomy Ecosystem</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Execution Action Flow
    if run_trigger:
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        status_box = st.empty()
        status_box.info(f"⏳ **Hierarchical Supervisor Initialized** — Formulating delegation strategy for: **'{target_query}'**...")

        tracker = BenchmarkTracker(output_path=str(benchmarks_json_path))
        tracker.start_workflow(query=target_query, model=GEMINI_MODEL)

        effective_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""

        with st.spinner("CrewAI Hierarchical Team executing: Lead Researcher ➔ Financial Analyst ➔ Technical Writer..."):
            report_markdown = ""
            if effective_key and not effective_key.startswith("your_"):
                try:
                    report_markdown = run_live_crew_workflow(
                        query=target_query,
                        csv_path=str(default_csv_path),
                        model=GEMINI_MODEL,
                        tracker=tracker,
                    )
                except Exception as exc:
                    st.warning(f"Live Crew API call warning: {exc}. Engaging offline tool execution pipeline.")
                    report_markdown = run_simulated_hierarchical_workflow(
                        query=target_query,
                        csv_path=str(default_csv_path),
                        tracker=tracker,
                    )
            else:
                report_markdown = run_simulated_hierarchical_workflow(
                    query=target_query,
                    csv_path=str(default_csv_path),
                    tracker=tracker,
                )

            # Persist Markdown
            with open(output_md_path, "w", encoding="utf-8") as f:
                f.write(report_markdown)

            # Compile Typeset A4 PDF
            generate_pdf_report(
                markdown_content=report_markdown,
                output_pdf_path=str(output_pdf_path),
                query=target_query,
                csv_path=str(default_csv_path),
            )

            tracker.finish_workflow(success=True)

        status_box.success(f"🎉 **Report Generation Complete!** A4 PDF compiled and metrics benchmarked.")

    # 3 Specialized Agent Showcase Grid
    st.markdown("### 🤖 Autonomous Hierarchical Agent Squad")
    ag_col1, ag_col2, ag_col3 = st.columns(3)

    with ag_col1:
        st.markdown(
            """
            <div class="agent-card">
                <div>
                    <div class="agent-header">
                        <span style="font-size: 1.5rem;">🔍</span>
                        <span class="status-pill status-ready"><span class="pulse-dot"></span> ACTIVE</span>
                    </div>
                    <div class="agent-title">Lead Researcher</div>
                    <div class="agent-role">Market Research Specialist</div>
                    <div class="agent-desc">Scrapes live web search networks (Tavily/Serper), gathers SEC disclosures, corporate press releases, and macroeconomic signals.</div>
                </div>
                <div style="font-size: 0.74rem; color: #64748B; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; margin-top: 8px;">
                    <b>Tools:</b> <code>web_scraper_tool</code>, <code>scrape_url</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with ag_col2:
        st.markdown(
            """
            <div class="agent-card">
                <div>
                    <div class="agent-header">
                        <span style="font-size: 1.5rem;">📊</span>
                        <span class="status-pill status-ready"><span class="pulse-dot"></span> ACTIVE</span>
                    </div>
                    <div class="agent-title">Data Analyst</div>
                    <div class="agent-role">Financial Data Analyst</div>
                    <div class="agent-desc">Ingests corporate metric matrices with Pandas, computes statistical summaries (mean, variance, quartiles), and generates clean Markdown tables.</div>
                </div>
                <div style="font-size: 0.74rem; color: #64748B; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; margin-top: 8px;">
                    <b>Tools:</b> <code>calculate_financial_metrics</code> (Pandas)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with ag_col3:
        st.markdown(
            """
            <div class="agent-card">
                <div>
                    <div class="agent-header">
                        <span style="font-size: 1.5rem;">✍️</span>
                        <span class="status-pill status-ready"><span class="pulse-dot"></span> ACTIVE</span>
                    </div>
                    <div class="agent-title">Content Writer</div>
                    <div class="agent-role">Technical Reports Writer</div>
                    <div class="agent-desc">Synthesizes scraped insights and quantitative data tables into an executive dossier, compiled into a publication-grade ReportLab A4 PDF.</div>
                </div>
                <div style="font-size: 0.74rem; color: #64748B; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; margin-top: 8px;">
                    <b>Compiler:</b> ReportLab Engine with Two-Pass Page X of Y
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# =============================================================================
# VIEW 2: FINANCIAL ANALYTICS (Plotly Interactive Visualizations)
# =============================================================================
elif nav_choice == "📈 Financial Analytics":
    st.markdown("## 📈 Quantitative Market Analytics Engine")
    st.markdown("Interactive descriptive statistical visualizations powered by **Pandas** and **Plotly**.")

    if default_csv_path.is_file():
        raw_df = get_raw_dataframe(str(default_csv_path))
        summary_df = get_summary_dataframe(str(default_csv_path))

        # Build Interactive Charts
        charts = create_financial_charts(raw_df)

        c1, c2 = st.columns(2)
        if "revenue" in charts:
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.plotly_chart(charts["revenue"], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if "scatter" in charts:
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.plotly_chart(charts["scatter"], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        if "pe" in charts:
            with c3:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.plotly_chart(charts["pe"], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if "capital" in charts:
            with c4:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.plotly_chart(charts["capital"], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### 📋 Pandas Statistical Summary Matrix")
        st.dataframe(summary_df, use_container_width=True)

        st.markdown("### 🗄️ Ingested Corporate Dataset")
        st.dataframe(raw_df, use_container_width=True)
    else:
        st.warning("No financial dataset found in data/sample_financials.csv.")

# =============================================================================
# VIEW 3: AGENT SWARM & LIVE ROUTING
# =============================================================================
elif nav_choice == "🤖 Agent Swarm & Routing":
    st.markdown("## 🤖 Hierarchical Agent Swarm & Delegation Audit")
    st.markdown("Inspect real-time agent coordination, latency metrics, and supervisor task routing.")

    if benchmarks_json_path.is_file():
        with open(benchmarks_json_path, "r", encoding="utf-8") as f:
            benchmarks_data = json.load(f)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Workflow Status", benchmarks_data.get("status", "SUCCESS"))
        m2.metric("Total Latency", f"{benchmarks_data.get('total_execution_time_seconds', 0)}s")
        m3.metric("Tasks Delegated", benchmarks_data.get("summary", {}).get("total_tasks", 0))
        m4.metric("Avg Task Latency", f"{benchmarks_data.get('summary', {}).get('average_task_latency_seconds', 0)}s")

        st.markdown("### ⏱️ Per-Agent Latency Benchmarks")
        tasks_list = benchmarks_data.get("task_benchmarks", [])
        if tasks_list:
            task_df = pd.DataFrame(tasks_list)
            st.dataframe(task_df[["task_name", "agent_role", "duration_seconds", "status"]], use_container_width=True)

        st.markdown("### 🗺️ Dynamic Task Routing History (Supervisor Log)")
        routing_steps = benchmarks_data.get("task_routing_history", [])
        for step in routing_steps:
            st.markdown(
                f"""
                <div class="timeline-item">
                    <span style="font-family: monospace; font-size: 0.88rem; color: #CBD5E1;">{step}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("### 📄 Raw benchmarks.json Payload")
        st.json(benchmarks_data)
    else:
        st.info("Execute a research query in the Research Workspace to view routing history.")

# =============================================================================
# VIEW 4: REPORT VAULT & PDF PREVIEW
# =============================================================================
elif nav_choice == "📑 Report Vault & PDF":
    st.markdown("## 📑 Generated Reports & PDF Vault")
    st.markdown("Preview, inspect, and download institutional A4 dossiers compiled by **ReportLab**.")

    col_md, col_pdf = st.columns([1, 1])

    with col_md:
        st.markdown("### 📝 Synthesized Markdown Dossier")
        if output_md_path.is_file():
            with open(output_md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            st.download_button(
                label="📥 Download Markdown (.md)",
                data=md_content,
                file_name="market_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.markdown('<div class="glass-card" style="max-height: 700px; overflow-y: auto;">', unsafe_allow_html=True)
            st.markdown(md_content)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No report generated yet.")

    with col_pdf:
        st.markdown("### 🏛️ Typeset A4 PDF Report")
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

            # Embedded PDF Viewer via base64 data URI
            base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_embed_html = (
                f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                f'width="100%" height="700" type="application/pdf" '
                f'style="border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">'
                f'</iframe>'
            )
            st.markdown(pdf_embed_html, unsafe_allow_html=True)
        else:
            st.info("No PDF compiled yet.")

# =============================================================================
# VIEW 5: PLATFORM SETTINGS
# =============================================================================
elif nav_choice == "⚙️ Platform Settings":
    st.markdown("## ⚙️ Platform & Model Configuration")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🧠 Model Selection & Inference Parameters")
    model_sel = st.selectbox(
        "Google Gemini Manager Model",
        options=["gemini/gemini-2.5-flash", "gemini/gemini-1.5-flash", "gemini/gemini-1.5-pro"],
        index=0,
    )
    temp_sel = st.slider("Temperature", min_value=0.0, max_value=1.0, value=TEMPERATURE, step=0.05)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🔑 Authentication Status")
    has_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if has_key:
        st.success("✅ GEMINI_API_KEY detected in environment configuration (.env). Live Crew execution active.")
    else:
        st.info("ℹ️ No GEMINI_API_KEY configured in .env. Resilient tool execution engine active.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📁 Runtime Storage Paths")
    st.markdown(f"- **Project Root:** `{PROJECT_ROOT}`")
    st.markdown(f"- **Dataset Directory:** `{DATA_DIR}`")
    st.markdown(f"- **Output Directory:** `{OUTPUT_DIR}`")
    st.markdown('</div>', unsafe_allow_html=True)
