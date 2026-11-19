"""CrewAI Task Definitions.

Defines the individual tasks delegated and coordinated by the hierarchical manager:
1. Research Task -> Lead Researcher ('Market Research Specialist')
2. Analysis Task -> Data Analyst ('Financial Data Analyst')
3. Writing Task -> Content Writer ('Technical Reports Writer')
"""

from crewai import Agent, Task


def create_research_task(agent: Agent, query: str) -> Task:
    """Create the market research task for the Lead Researcher."""
    return Task(
        description=(
            f"Conduct comprehensive market research on '{query}'. "
            "1. Search financial data networks and scrape live industry disclosures and filings.\n"
            "2. Identify top performing companies, quarterly revenue trajectories, and macro catalysts.\n"
            "3. Document specific revenue figures, margin expansions, and strategic shifts.\n"
            "4. Provide a structured research briefing with verified facts and market signals."
        ),
        expected_output=(
            "A structured market intelligence briefing detailing key industry players, "
            "growth drivers, recent financial performance figures, and competitive dynamics."
        ),
        agent=agent,
    )


def create_analysis_task(agent: Agent, csv_path: str, query: str) -> Task:
    """Create the quantitative financial analysis task for the Data Analyst."""
    return Task(
        description=(
            f"Analyze the financial metrics dataset for '{query}'.\n"
            f"1. Use the 'calculate_financial_metrics' tool with csv_path='{csv_path}' "
            "to load corporate metrics and compute statistical summaries (mean, min, max, standard deviation).\n"
            "2. Verify numeric consistency across revenue, margins, P/E multiples, and cash flows.\n"
            "3. Format the statistical results into a clean Markdown table.\n"
            "4. Highlight top quartiles, margin outliers, and growth benchmarks."
        ),
        expected_output=(
            "A thorough financial analytics section featuring the summary statistics Markdown table, "
            "interpretation of mean and variance across peers, and valuation highlights."
        ),
        agent=agent,
    )


def create_writing_task(agent: Agent, query: str) -> Task:
    """Create the report synthesis task for the Content Writer."""
    return Task(
        description=(
            f"Synthesize the research findings and quantitative data analysis for '{query}' "
            "into a comprehensive, executive-level technical market research report.\n"
            "Structure the report with the following mandatory sections:\n"
            "# Market Research Dossier: {query}\n"
            "## 1. Executive Summary\n"
            "## 2. Sector Overview & Market Dynamics\n"
            "## 3. Quantitative Financial Analysis & Statistical Summary (MUST include the Markdown statistics table)\n"
            "## 4. Competitive Benchmarking & Peer Comparisons\n"
            "## 5. Risk Assessment & Strategic Outlook\n"
            "Ensure copy is lucid, analytical, objective, and professionally structured."
        ),
        expected_output=(
            "A complete, publication-grade market research report in clean Markdown format with all "
            "sections, numerical tables, and strategic recommendations."
        ),
        agent=agent,
    )
