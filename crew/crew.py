"""Hierarchical Crew Orchestration Module.

Configures and manages the multi-agent crew with Process.hierarchical,
delegating tasks dynamically via a supervisor manager_llm powered by Google Gemini.
"""

from typing import Dict, Any, Optional
from crewai import Crew, Process
from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    VERBOSE,
    DATA_DIR
)
from crew.agents import (
    get_gemini_llm,
    create_lead_researcher,
    create_data_analyst,
    create_content_writer,
)
from crew.tasks import (
    create_research_task,
    create_analysis_task,
    create_writing_task,
)


def build_market_research_crew(
    query: str,
    csv_path: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Assembles and returns the Hierarchical Crew with Gemini Manager LLM.
    
    Args:
        query (str): The research topic / target market query.
        csv_path (str, optional): Path to the corporate financials CSV.
        api_key (str, optional): Gemini API key override.
        model (str, optional): Gemini model override.
        
    Returns:
        dict: Dictionary containing initialized crew, agents, tasks, and manager_llm.
    """
    effective_csv = csv_path or str(DATA_DIR / "sample_financials.csv")
    manager_llm = get_gemini_llm(model=model, api_key=api_key)
    
    # Instantiate Specialized Agents
    researcher = create_lead_researcher(llm=manager_llm)
    analyst = create_data_analyst(llm=manager_llm)
    writer = create_content_writer(llm=manager_llm)
    
    # Instantiate Tasks
    task_research = create_research_task(researcher, query=query)
    task_analysis = create_analysis_task(analyst, csv_path=effective_csv, query=query)
    task_writing = create_writing_task(writer, query=query)
    
    agents = [researcher, analyst, writer]
    tasks = [task_research, task_analysis, task_writing]
    
    # Configure Crew with Hierarchical Process and Manager LLM
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.hierarchical,
        manager_llm=manager_llm,
        verbose=VERBOSE,
    )
    
    return {
        "crew": crew,
        "agents": {
            "researcher": researcher,
            "analyst": analyst,
            "writer": writer,
        },
        "tasks": {
            "research": task_research,
            "analysis": task_analysis,
            "writing": task_writing,
        },
        "manager_llm": manager_llm,
        "query": query,
        "csv_path": effective_csv,
    }
