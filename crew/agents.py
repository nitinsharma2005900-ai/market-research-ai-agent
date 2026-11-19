"""CrewAI Agent Definitions.

Configures the three specialized agents managed hierarchically:
1. Lead Researcher ('Market Research Specialist')
2. Data Analyst ('Financial Data Analyst')
3. Content Writer ('Technical Reports Writer')
"""

from typing import Optional
from crewai import Agent, LLM
from config.settings import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, VERBOSE
from crew.tools.financial_parser import calculate_financial_metrics
from crew.tools.scraper_tool import web_scraper_tool, scrape_webpage_content


def get_gemini_llm(model: Optional[str] = None, api_key: Optional[str] = None) -> LLM:
    """Instantiate and return CrewAI LLM configured for Google Gemini."""
    effective_model = model or GEMINI_MODEL
    effective_key = api_key or GEMINI_API_KEY
    
    # LiteLLM expects 'gemini/<model_name>' format
    if not effective_model.startswith("gemini/"):
        effective_model = f"gemini/{effective_model}"
        
    return LLM(
        model=effective_model,
        api_key=effective_key,
        temperature=TEMPERATURE,
    )


def create_lead_researcher(llm: Optional[LLM] = None) -> Agent:
    """Creates the Lead Researcher Agent."""
    return Agent(
        role="Market Research Specialist",
        goal="Query search search networks, locate financial data, and scrape company metrics.",
        backstory=(
            "You are a premier market research specialist with over a decade of experience tracking "
            "corporate disclosures, SEC filings, tech earnings, and macroeconomic shifts. Your mission "
            "is to uncover actionable market data, identify key industry developments, and gather raw "
            "corporate performance figures."
        ),
        tools=[web_scraper_tool, scrape_webpage_content],
        llm=llm or get_gemini_llm(),
        verbose=VERBOSE,
        memory=True,
        allow_delegation=False,
    )


def create_data_analyst(llm: Optional[LLM] = None) -> Agent:
    """Creates the Financial Data Analyst Agent."""
    return Agent(
        role="Financial Data Analyst",
        goal="Parse data matrices using Pandas, compute averages, and verify numeric consistency.",
        backstory=(
            "You are a meticulous financial quantitative analyst. You receive corporate data points and "
            "CSV files, use Pandas to compute summary statistics (mean, median, standard deviation, min, max), "
            "and rigorously verify the consistency and significance of financial metrics. You output "
            "structured Markdown tables for executive reporting."
        ),
        tools=[calculate_financial_metrics],
        llm=llm or get_gemini_llm(),
        verbose=VERBOSE,
        memory=True,
        allow_delegation=False,
    )


def create_content_writer(llm: Optional[LLM] = None) -> Agent:
    """Creates the Technical Reports Writer Agent."""
    return Agent(
        role="Technical Reports Writer",
        goal="Synthesize information, write sections, and structure copy.",
        backstory=(
            "You are a senior technical writer and financial editor who produces executive-grade market "
            "research dossiers. You seamlessly synthesize market research findings and quantitative "
            "Pandas metrics into clear, articulate, and compelling structured reports featuring Executive "
            "Summaries, Market Dynamics, Financial Analysis, and Strategic Outlooks."
        ),
        tools=[],
        llm=llm or get_gemini_llm(),
        verbose=VERBOSE,
        memory=True,
        allow_delegation=False,
    )
