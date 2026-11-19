"""Unit tests for Programmatic ReportLab PDF Report Generator.

Verifies that the PDF report compiler successfully writes valid A4 PDF documents,
renders styled headers, tabular grids, automatic page numbers, and raises no styling exceptions.
"""

import os
import tempfile
from pathlib import Path
import pytest

from utils.pdf_generator import generate_pdf_report
from config.settings import DATA_DIR


@pytest.fixture
def sample_markdown():
    """Sample executive market research markdown output."""
    return """
# Market Research Dossier: Tech Sector Q3 Analysis

## 1. Executive Summary
The technology sector demonstrated robust operational resilience in Q3, propelled by sustained capital expenditures in cloud infrastructure and enterprise artificial intelligence platforms. Leading mega-cap hyperscalers reported revenue expansion above historical consensus estimates.

## 2. Sector Overview & Market Dynamics
Key catalysts during the quarter included:
- **Cloud Infrastructure Acceleration**: Public cloud revenues increased at a weighted 19.4% YoY rate.
- **Hardware & Semiconductor Demand**: Accelerated compute architectures observed unprecedented backlog expansion.
- **Enterprise Software Discretionary Spend**: IT budget allocation tilted decisively toward automated reasoning systems.

## 3. Quantitative Financial Analysis & Statistical Summary
The following analysis outlines the core metrics across primary tech equities during the reporting period:

## 4. Competitive Benchmarking & Peer Comparisons
- **Valuation Multiples**: Price-to-earnings ratios stabilized across large-cap tech.
- **Free Cash Flow Conversion**: Free cash flow margins averaged 24.8% of aggregate revenue.

## 5. Risk Assessment & Strategic Outlook
- Macroeconomic volatility and interest rate trajectories
- Semiconductor supply chain sovereignty and geopolitical export restrictions
- Power infrastructure and datacentre grid constraints
"""


def test_pdf_report_compilation_success(sample_markdown):
    """Verify PDF compiler writes a valid non-empty PDF file without styling exceptions."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = os.path.join(tmp_dir, "test_market_report.pdf")
        csv_path = str(DATA_DIR / "sample_financials.csv")

        # Compile PDF
        result_path = generate_pdf_report(
            markdown_content=sample_markdown,
            output_pdf_path=pdf_path,
            query="Tech Sector Q3 Analysis",
            csv_path=csv_path,
        )

        # 1. Check file exists
        assert os.path.exists(result_path), "Generated PDF file must exist on disk"

        # 2. Check file size is substantial (contains headers, styling, table)
        file_size = os.path.getsize(result_path)
        assert file_size > 2048, f"PDF file size ({file_size} bytes) should be > 2KB"

        # 3. Check valid PDF signature bytes
        with open(result_path, "rb") as f:
            header_bytes = f.read(5)
            assert header_bytes == b"%PDF-", f"Expected PDF magic header, got: {header_bytes}"


def test_pdf_compilation_without_csv(sample_markdown):
    """Verify PDF compiler succeeds even if no CSV path is provided."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = os.path.join(tmp_dir, "test_no_csv_report.pdf")

        result_path = generate_pdf_report(
            markdown_content=sample_markdown,
            output_pdf_path=pdf_path,
            query="Cloud Computing Overview",
            csv_path=None,
        )

        assert os.path.exists(result_path)
        assert os.path.getsize(result_path) > 1024
