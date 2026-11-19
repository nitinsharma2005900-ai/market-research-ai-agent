"""ZIP Archiver Utility for Market Research AI Agent.

Packages the complete project into a clean, portable ZIP archive,
excluding large virtual environments (.venv), git directories, and caches.
"""

import os
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ZIP_OUTPUT = PROJECT_ROOT.parent / "Market_Research_AI_Agent.zip"

EXCLUDE_DIRS = {".venv", "__pycache__", ".git", ".pytest_cache"}
EXCLUDE_EXTS = {".pyc", ".pyo"}


def create_clean_zip():
    print(f"Zipping project: {PROJECT_ROOT} -> {ZIP_OUTPUT}")
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in EXCLUDE_EXTS:
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(PROJECT_ROOT)
                zipf.write(file_path, arcname)

    size_kb = os.path.getsize(ZIP_OUTPUT) / 1024
    print(f"Archive created successfully: {ZIP_OUTPUT} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    create_clean_zip()
