"""Unit tests for Execution Benchmarking & Analytics Tracker."""

import json
import os
import tempfile
import time
import pytest

from utils.benchmark import BenchmarkTracker


def test_benchmark_tracker_workflow_and_json_persistence():
    """Verify BenchmarkTracker logs task metrics and writes valid JSON."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        json_path = os.path.join(tmp_dir, "benchmarks.json")
        tracker = BenchmarkTracker(output_path=json_path)

        tracker.start_workflow("Tech Sector Q3 Analysis", model="gemini/gemini-2.5-flash")
        
        # Simulate Task 1
        tracker.start_task("Market Research", "Market Research Specialist")
        time.sleep(0.05)
        tracker.finish_task("Market Research", "Market Research Specialist", success=True)

        # Simulate Task 2
        tracker.start_task("Financial Analysis", "Financial Data Analyst")
        time.sleep(0.05)
        tracker.finish_task("Financial Analysis", "Financial Data Analyst", success=True)

        metrics = tracker.finish_workflow(success=True)

        # Assertions
        assert os.path.exists(json_path)
        assert metrics["status"] == "SUCCESS"
        assert metrics["query"] == "Tech Sector Q3 Analysis"
        assert metrics["llm_model"] == "gemini/gemini-2.5-flash"
        assert len(metrics["task_benchmarks"]) == 2
        assert len(metrics["task_routing_history"]) >= 4
        assert metrics["total_execution_time_seconds"] >= 0.1

        # Verify JSON file on disk
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["summary"]["total_tasks"] == 2
            assert data["task_benchmarks"][0]["agent_role"] == "Market Research Specialist"
