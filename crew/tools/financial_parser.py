"""Financial Data Parser Tool.

Loads corporate metrics from CSV, computes summary statistics (mean, min, max, std),
and returns clean Markdown tables for agent consumption and report generation.
"""

from pathlib import Path
import pandas as pd
from crewai.tools import tool
from config.settings import DATA_DIR, PROJECT_ROOT


def resolve_csv_path(csv_path: str) -> Path:
    """Resolve csv path whether given as absolute, relative, or just filename."""
    path = Path(csv_path)
    if path.is_file():
        return path
    
    # Try relative to project root
    candidate = PROJECT_ROOT / path
    if candidate.is_file():
        return candidate
    
    # Try in data directory
    candidate = DATA_DIR / path.name
    if candidate.is_file():
        return candidate
        
    # Default fallback to sample_financials.csv
    fallback = DATA_DIR / "sample_financials.csv"
    if fallback.is_file():
        return fallback

    raise FileNotFoundError(f"CSV file not found at: {csv_path}")


@tool("calculate_financial_metrics")
def calculate_financial_metrics(csv_path: str) -> str:
    """Loads corporate metrics from CSV and returns summary statistics as Markdown.
    
    Args:
        csv_path (str): File path to the financial CSV dataset.
        
    Returns:
        str: Clean Markdown table of summary statistics (count, mean, std, min, 25%, 50%, 75%, max).
    """
    resolved_path = resolve_csv_path(csv_path)
    df = pd.read_csv(resolved_path)
    
    # Select numeric columns for statistical summary
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        summary = df.describe().to_markdown()
    else:
        summary = numeric_df.describe().round(2).to_markdown()
        
    return summary


def get_raw_dataframe(csv_path: str) -> pd.DataFrame:
    """Helper to return raw pandas DataFrame from CSV path."""
    resolved_path = resolve_csv_path(csv_path)
    return pd.read_csv(resolved_path)


def get_summary_dataframe(csv_path: str) -> pd.DataFrame:
    """Helper to return the describe() DataFrame with calculated metrics."""
    df = get_raw_dataframe(csv_path)
    numeric_df = df.select_dtypes(include=["number"])
    return numeric_df.describe().round(2)
