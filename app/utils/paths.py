from __future__ import annotations

from pathlib import Path

APP_NAME = "F5Narrator"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
CACHE_DIR = PROJECT_ROOT / "cache"
EXPORTS_DIR = PROJECT_ROOT / "exports"
PROJECTS_DIR = PROJECT_ROOT / "projects"


def ensure_runtime_directories() -> None:
    for directory in (CONFIG_DIR, CACHE_DIR, EXPORTS_DIR, PROJECTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
