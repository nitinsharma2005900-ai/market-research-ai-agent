"""Execution Benchmarking and Routing Analytics Module.

Captures, traces, and persists runtime performance metrics to benchmarks.json:
- Execution latency per agent task
- Total workflow turnaround time
- Hierarchical task routing history
- Execution environment metadata
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class BenchmarkTracker:
    """Tracks agent execution metrics, task routing, and latencies."""

    def __init__(self, output_path: Optional[str] = None):
        self.output_path = Path(output_path) if output_path else Path("output/benchmarks.json")
        self.workflow_start_time: Optional[float] = None
        self.workflow_end_time: Optional[float] = None
        self.query: str = ""
        self.model: str = ""
        self.tasks: List[Dict[str, Any]] = []
        self.task_routing_history: List[str] = []
        self._current_task: Optional[Dict[str, Any]] = None

    def start_workflow(self, query: str, model: str = "gemini/gemini-2.5-flash"):
        """Marks workflow initialization."""
        self.workflow_start_time = time.time()
        self.query = query
        self.model = model
        self.task_routing_history.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Manager LLM initialized workflow for: '{query}'"
        )

    def start_task(self, task_name: str, agent_role: str):
        """Marks start of a delegated agent task."""
        now = time.time()
        self._current_task = {
            "task_name": task_name,
            "agent_role": agent_role,
            "start_time": now,
            "start_iso": datetime.now().isoformat(),
        }
        self.task_routing_history.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Manager LLM -> Delegated to '{agent_role}' for '{task_name}'"
        )

    def finish_task(self, task_name: str, agent_role: str, success: bool = True):
        """Marks completion of an agent task and calculates latency."""
        now = time.time()
        start = self._current_task["start_time"] if self._current_task else now
        duration = round(now - start, 3)

        record = {
            "task_name": task_name,
            "agent_role": agent_role,
            "duration_seconds": duration,
            "status": "COMPLETED" if success else "FAILED",
            "completed_iso": datetime.now().isoformat(),
        }
        self.tasks.append(record)
        self.task_routing_history.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] '{agent_role}' completed '{task_name}' in {duration}s"
        )
        self._current_task = None

    def finish_workflow(self, success: bool = True) -> Dict[str, Any]:
        """Calculates total workflow duration and persists metrics to JSON."""
        self.workflow_end_time = time.time()
        total_duration = round(
            (self.workflow_end_time - (self.workflow_start_time or self.workflow_end_time)), 3
        )

        self.task_routing_history.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Workflow finished successfully. Total duration: {total_duration}s"
        )

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "query": self.query,
            "llm_model": self.model,
            "status": "SUCCESS" if success else "FAILED",
            "total_execution_time_seconds": total_duration,
            "task_benchmarks": self.tasks,
            "task_routing_history": self.task_routing_history,
            "summary": {
                "total_tasks": len(self.tasks),
                "average_task_latency_seconds": (
                    round(sum(t["duration_seconds"] for t in self.tasks) / len(self.tasks), 3)
                    if self.tasks
                    else 0.0
                ),
            },
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        return metrics
