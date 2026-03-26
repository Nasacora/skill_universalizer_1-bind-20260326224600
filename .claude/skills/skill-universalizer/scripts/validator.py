"""
validator.py — Valida que una variante generada es correcta.
"""
import re
from datetime import datetime
from pathlib import Path

import yaml


class SkillValidator:
    """
    Valida que una variante generada por VariantGenerator cumple
    todos los requisitos para ser publicada.
    """

    ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]+$")
    ABS_PATH_PATTERNS = ["/home/", "/Users/", "C:\\", "C:/"]
    MIN_CONTENT_LINES = 10

    def __init__(self, platform_profiles_path: Path = None):
        if platform_profiles_path is None:
            platform_profiles_path = (
                Path(__file__).parent.parent / "config" / "platform-profiles.yaml"
            )
        self._profiles_path = Path(platform_profiles_path)
        self._known_platforms: set = set()
        self._load_known_platforms()
        self.errors: list = []

    def validate(self, variant: dict, platform: str) -> bool:
        """Valida una variante. Retorna True si válida."""
        self.errors = []

        if not isinstance(variant, dict):
            self.errors.append("variant debe ser un dict")
            return False

        skill_id = variant.get("skill_id", "")
        if not skill_id:
            self.errors.append("Falta 'skill_id' en la variante")
        elif not self.ID_PATTERN.match(str(skill_id)):
            self.errors.append(
                f"skill_id inválido (debe ser kebab-case): '{skill_id}'"
            )

        if platform not in self._known_platforms:
            self.errors.append(
                f"Plataforma desconocida: '{platform}'. "
                f"Conocidas: {sorted(self._known_platforms)}"
            )

        content = variant.get("skill_md_content", "")
        if not content or not content.strip():
            self.errors.append("skill_md_content está vacío")
            return False

        for abs_pattern in self.ABS_PATH_PATTERNS:
            if abs_pattern in content:
                self.errors.append(
                    f"skill_md_content contiene path absoluto: '{abs_pattern}'"
                )

        line_count = len(content.strip().splitlines())
        if line_count < self.MIN_CONTENT_LINES:
            self.errors.append(
                f"skill_md_content tiene solo {line_count} líneas "
                f"(mínimo: {self.MIN_CONTENT_LINES})"
            )

        generated_at = variant.get("generated_at", "")
        if not generated_at:
            self.errors.append("Falta 'generated_at' en la variante")
        else:
            try:
                datetime.fromisoformat(str(generated_at).replace("Z", "+00:00"))
            except ValueError:
                self.errors.append(
                    f"generated_at no es un timestamp ISO 8601 válido: '{generated_at}'"
                )

        return len(self.errors) == 0

    def _load_known_platforms(self) -> None:
        try:
            if self._profiles_path.exists():
                with open(self._profiles_path, "r", encoding="utf-8") as f:
                    profiles = yaml.safe_load(f) or {}
                self._known_platforms = set(profiles.keys())
        except Exception:
            pass

        if not self._known_platforms:
            self._known_platforms = {"claude", "codex", "cursor", "gemini"}
