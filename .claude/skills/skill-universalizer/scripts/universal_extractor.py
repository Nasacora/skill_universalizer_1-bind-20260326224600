"""
universal_extractor.py — Extrae el contenido universal de la skill.
"""
from pathlib import Path

import yaml


class UniversalExtractor:
    """
    Extrae el contenido universal de una skill: lo que es igual
    para todas las plataformas destino.
    """

    EXCLUDED_PATTERNS = {
        "__pycache__", ".git", ".DS_Store", ".pytest_cache",
    }
    EXCLUDED_SUFFIXES = {".pyc", ".tmp", ".bak"}

    def __init__(self):
        self._last_error: str = ""

    def extract(self, skill_path: Path, metadata: dict):
        """Extrae el contenido universal de la skill. Retorna dict o None."""
        skill_path = Path(skill_path)

        try:
            core_file = metadata.get("core", "SKILL.md")
            core_path = skill_path / core_file
            if not core_path.exists():
                self._last_error = f"No se encontró el archivo core: {core_path}"
                return None

            core_content = core_path.read_text(encoding="utf-8")

            scripts_dir = skill_path / "scripts"
            scripts = []
            if scripts_dir.exists() and scripts_dir.is_dir():
                scripts = [
                    str(f.relative_to(skill_path))
                    for f in sorted(scripts_dir.rglob("*"))
                    if f.is_file() and not self._is_excluded(f)
                ]

            config_dir = skill_path / "config"
            config_files = []
            if config_dir.exists() and config_dir.is_dir():
                config_files = [
                    str(f.relative_to(skill_path))
                    for f in sorted(config_dir.rglob("*"))
                    if f.is_file() and not self._is_excluded(f)
                ]

            has_tests = (skill_path / "tests").exists()
            has_docs = (skill_path / "docs").exists()

            return {
                "skill_id": metadata.get("id", ""),
                "name": metadata.get("name", ""),
                "description": metadata.get("description", ""),
                "core_content": core_content,
                "scripts": scripts,
                "config_files": config_files,
                "has_tests": has_tests,
                "has_docs": has_docs,
                "keywords": metadata.get("keywords", []),
                "agent": metadata.get("agent", None),
                "version": metadata.get("version", "1.0.0"),
            }

        except Exception as exc:
            self._last_error = f"Error extrayendo contenido universal: {exc}"
            return None

    @property
    def last_error(self) -> str:
        return self._last_error

    def _is_excluded(self, path: Path) -> bool:
        for part in path.parts:
            if part in self.EXCLUDED_PATTERNS:
                return True
        if path.suffix in self.EXCLUDED_SUFFIXES:
            return True
        return False
