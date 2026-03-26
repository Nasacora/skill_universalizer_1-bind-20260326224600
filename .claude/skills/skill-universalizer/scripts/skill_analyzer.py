"""
skill_analyzer.py — Analiza la estructura de una skill y verifica que es universalizable.
"""
import re
from pathlib import Path

import yaml


class SkillAnalyzer:
    """
    Analiza la estructura de una skill y verifica que cumple el contrato
    necesario para ser universalizada.
    """

    ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]+$")
    REQUIRED_FIELDS = ["id", "name", "core", "providers"]

    def __init__(self):
        self.errors: list = []
        self.skill_id: str = ""
        self.metadata: dict = {}
        self.current_platforms: list = []
        self._valid: bool = False

    def analyze(self, skill_path: Path) -> None:
        """Ejecuta el análisis completo de la skill en skill_path."""
        self.errors = []
        self.skill_id = ""
        self.metadata = {}
        self.current_platforms = []
        self._valid = False

        skill_path = Path(skill_path)

        if not skill_path.exists():
            self.errors.append(f"El directorio no existe: {skill_path}")
            return
        if not skill_path.is_dir():
            self.errors.append(f"La ruta no es un directorio: {skill_path}")
            return

        yaml_path = skill_path / "skill.yaml"
        if not yaml_path.exists():
            self.errors.append("Falta skill.yaml en la raíz de la skill")
            return

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                self.metadata = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            self.errors.append(f"skill.yaml no es YAML válido: {exc}")
            return

        if not isinstance(self.metadata, dict):
            self.errors.append("skill.yaml debe ser un mapa YAML (dict)")
            return

        for field in self.REQUIRED_FIELDS:
            if field not in self.metadata:
                self.errors.append(f"Campo obligatorio ausente en skill.yaml: '{field}'")

        if self.errors:
            return

        skill_id = self.metadata.get("id", "")
        if not self.ID_PATTERN.match(str(skill_id)):
            self.errors.append(
                f"El campo 'id' debe ser kebab-case (^[a-z][a-z0-9-]+$), "
                f"recibido: '{skill_id}'"
            )
            return
        self.skill_id = skill_id

        core_file = self.metadata.get("core", "")
        core_path = skill_path / core_file
        if not core_path.exists():
            self.errors.append(
                f"El archivo core '{core_file}' indicado en skill.yaml no existe"
            )

        providers = self.metadata.get("providers", {})
        if not isinstance(providers, dict) or len(providers) == 0:
            self.errors.append(
                "skill.yaml debe declarar al menos un provider en 'providers:'"
            )
            return

        for platform_key, provider_info in providers.items():
            if not isinstance(provider_info, dict):
                self.errors.append(
                    f"providers.{platform_key} debe ser un mapa con 'frontmatter:'"
                )
                continue
            frontmatter_rel = provider_info.get("frontmatter", "")
            if not frontmatter_rel:
                self.errors.append(
                    f"providers.{platform_key} no tiene campo 'frontmatter'"
                )
                continue
            frontmatter_path = skill_path / frontmatter_rel
            if not frontmatter_path.exists():
                self.errors.append(
                    f"Provider '{platform_key}': archivo '{frontmatter_rel}' no encontrado"
                )

        self.current_platforms = list(self.metadata.get("platforms", []))
        self._valid = len(self.errors) == 0

    def is_valid(self) -> bool:
        """Retorna True si la skill pasó todas las validaciones."""
        return self._valid
