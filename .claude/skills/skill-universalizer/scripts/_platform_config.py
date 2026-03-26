"""
Auto-detección de plataforma de ejecución.
Importar en scripts que necesiten paths adaptativos.
"""
import os
from pathlib import Path


def detect_platform() -> str:
    """
    Detecta en qué plataforma de IA está ejecutándose.
    Retorna: 'claude' | 'codex' | 'cursor' | 'gemini' | 'unknown'
    """
    if os.getenv("CLAUDE_PROJECT_DIR") or os.getenv("CLAUDE_CODE"):
        return "claude"
    if os.getenv("CODEX_PROJECT_DIR"):
        return "codex"
    if os.getenv("CURSOR_PROJECT_DIR"):
        return "cursor"
    if os.getenv("GEMINI_PROJECT_DIR"):
        return "gemini"

    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".claude").exists():
            return "claude"
        if (parent / ".codex").exists():
            return "codex"
        if (parent / ".cursor").exists():
            return "cursor"
        if (parent / ".gemini").exists():
            return "gemini"
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            break

    return "unknown"


def get_skill_root(platform: str = None) -> Path:
    """Retorna la ruta raíz de la skill actual."""
    if platform is None:
        platform = detect_platform()
    return Path(__file__).parent.parent


def get_project_root() -> Path:
    """Retorna la raíz del proyecto."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".claude").exists() or (parent / ".codex").exists():
            return parent
        if (parent / ".git").exists():
            return parent
    return cwd


def get_shared_artifacts(skill_id: str) -> Path:
    """Retorna la ruta de shared_artifacts para una skill."""
    return get_project_root() / "shared_artifacts" / skill_id
