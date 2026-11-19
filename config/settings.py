"""Settings and Configuration Module.

Handles environment variable loading, model selection, directory paths,
and API key discovery.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env file
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Primary Gemini Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-3.7-flash")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
VERBOSE = os.getenv("VERBOSE", "True").lower() in ("true", "1", "yes")

# Sync GEMINI_API_KEY into environment for LiteLLM / CrewAI / Google SDK
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    if not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
