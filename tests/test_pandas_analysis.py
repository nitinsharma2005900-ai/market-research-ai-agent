"""Unit tests for Pandas Financial Data Parser Tool.

Verifies that the financial data parser correctly calculates summary statistics
(mean, min, max, standard deviations) on mock CSV datasets and returns clean Markdown tables.
"""

import os
import tempfile
import pandas as pd
import pytest

from crew.tools.financial_parser import (
    calculate_financial_metrics,
    get_summary_dataframe,
    get_raw_dataframe,
)


@pytest.fixture
def mock_csv_file():
    """Create a temporary mock CSV file with deterministic corporate metrics."""
    data = {
        "Company": ["TechA", "TechB", "TechC", "TechD"],
        "Revenue_B": [100.0, 200.0, 300.0, 400.0],
        "Net_Margin_Pct": [10.0, 20.0, 30.0, 40.0],
        "PE_Ratio": [15.0, 25.0, 35.0, 45.0],
        "Free_Cash_Flow_B": [5.0, 15.0, 25.0, 35.0],
    }
    df = pd.DataFrame(data)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_calculate_financial_metrics_math_accuracy(mock_csv_file):
    """Verify tool calculates mathematically exact statistics on mock dataset."""
    # Call the tool function (crewai tool decorator wraps function)
    result = (
        calculate_financial_metrics.run(mock_csv_file)
        if hasattr(calculate_financial_metrics, "run")
        else calculate_financial_metrics(mock_csv_file)
    )

    assert isinstance(result, str)
    assert "|" in result, "Result must contain Markdown table pipe characters"
    assert "mean" in result.lower(), "Markdown table must contain 'mean' statistic"
    assert "std" in result.lower(), "Markdown table must contain 'std' statistic"
    assert "min" in result.lower(), "Markdown table must contain 'min' statistic"
    assert "max" in result.lower(), "Markdown table must contain 'max' statistic"

    # Verify mathematical accuracy of mean: (100+200+300+400)/4 = 250.0
    assert "250" in result, "Revenue mean of 250 must be present in output table"
    # Verify min is 100
    assert "100" in result
    # Verify max is 400
    assert "400" in result


def test_get_summary_dataframe_shape(mock_csv_file):
    """Verify get_summary_dataframe returns proper describe structure."""
    summary_df = get_summary_dataframe(mock_csv_file)

    assert isinstance(summary_df, pd.DataFrame)
    # Four numeric columns
    assert "Revenue_B" in summary_df.columns
    assert "Net_Margin_Pct" in summary_df.columns
    assert "PE_Ratio" in summary_df.columns
    assert "Free_Cash_Flow_B" in summary_df.columns
    # Non-numeric Company column should be excluded
    assert "Company" not in summary_df.columns

    # Check describe rows
    expected_rows = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    for row_name in expected_rows:
        assert row_name in summary_df.index

    # Check exact computed values
    assert summary_df.loc["mean", "Revenue_B"] == 250.0
    assert summary_df.loc["min", "Revenue_B"] == 100.0
    assert summary_df.loc["max", "Revenue_B"] == 400.0
    assert summary_df.loc["count", "Revenue_B"] == 4.0


def test_raw_dataframe_loading(mock_csv_file):
    """Verify raw dataframe matches input rows."""
    raw_df = get_raw_dataframe(mock_csv_file)
    assert len(raw_df) == 4
    assert list(raw_df["Company"]) == ["TechA", "TechB", "TechC", "TechD"]


def test_missing_file_raises_error():
    """Verify parser raises FileNotFoundError when given non-existent file."""
    with pytest.raises(FileNotFoundError):
        calculate_financial_metrics.run("non_existent_fake_dataset_xyz.csv")
