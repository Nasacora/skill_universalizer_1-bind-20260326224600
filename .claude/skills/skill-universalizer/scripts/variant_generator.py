"""
variant_generator.py — Genera una variante de SKILL.md para una plataforma específica.
"""
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class VariantGenerator:
    """
    Genera variantes de SKILL.md para una plataforma concreta,
    combinando el core universal con el provider específico.
    """

    KNOWN_PLATFORMS = {"claude", "codex", "cursor", "gemini"}

    def __init__(self, templates_dir: Path = None, skill_path: Path = None):
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        self._templates_dir = Path(templates_dir)
        self._skill_path = Path(skill_path) if skill_path else None
        self._last_error: str = ""

        self._jinja_env = Environment(
            loader=FileSystemLoader(str(self._templates_dir)),
            autoescape=False,
            keep_trailing_newline=True,
        )

    def generate(self, skill_id: str, universal: dict, metadata: dict, platform: str, skill_path: Path = None):
        """Genera la variante para una plataforma. Retorna dict o None."""
        if platform not in self.KNOWN_PLATFORMS:
            self._last_error = (
                f"Plataforma desconocida: '{platform}'. "
                f"Soportadas: {sorted(self.KNOWN_PLATFORMS)}"
            )
            return None

        effective_skill_path = Path(skill_path) if skill_path else self._skill_path
        if effective_skill_path is None:
            self._last_error = "skill_path no especificado"
            return None

        try:
            provider_meta = self._load_provider(effective_skill_path, metadata, platform)
            if provider_meta is None:
                return None

            template = self._load_template(platform)
            context = self._build_context(skill_id, universal, metadata, platform, provider_meta)
            skill_md_content = template.render(**context)

            return {
                "skill_id": skill_id,
                "platform": platform,
                "skill_md_content": skill_md_content,
                "provider_meta": provider_meta,
                "generated_at": context["generated_at"],
            }

        except Exception as exc:
            self._last_error = f"Error generando variante para '{platform}': {exc}"
            return None

    @property
    def last_error(self) -> str:
        return self._last_error

    def _load_provider(self, skill_path: Path, metadata: dict, platform: str):
        providers = metadata.get("providers", {})
        provider_info = providers.get(platform, {})

        if not provider_info:
            return {}

        frontmatter_rel = provider_info.get("frontmatter", "")
        if not frontmatter_rel:
            self._last_error = f"providers.{platform} no tiene campo 'frontmatter'"
            return None

        frontmatter_path = skill_path / frontmatter_rel
        if not frontmatter_path.exists():
            self._last_error = f"Archivo de provider no encontrado: {frontmatter_path}"
            return None

        try:
            with open(frontmatter_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            self._last_error = f"YAML inválido en {frontmatter_path}: {exc}"
            return None

    def _load_template(self, platform: str):
        template_name = f"SKILL_{platform.upper()}.md.j2"
        try:
            return self._jinja_env.get_template(template_name)
        except TemplateNotFound:
            return self._jinja_env.get_template("SKILL_BASE.md.j2")

    def _build_context(self, skill_id, universal, metadata, platform, provider_meta) -> dict:
        return {
            "skill_id": skill_id,
            "name": universal.get("name", ""),
            "description": universal.get("description", ""),
            "core_content": universal.get("core_content", ""),
            "version": universal.get("version", "1.0.0"),
            "platform": platform,
            "keywords": universal.get("keywords", []),
            "agent": universal.get("agent"),
            "when_to_use": metadata.get("when_to_use", ""),
            "trigger": provider_meta.get("trigger", ""),
            "model": provider_meta.get("model", self._default_model(platform)),
            "hooks": provider_meta.get("hooks", []),
            "notes": provider_meta.get("notes", ""),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _default_model(self, platform: str) -> str:
        defaults = {
            "claude": "claude-haiku-4-5",
            "codex": "gpt-4o",
            "cursor": "claude-sonnet-4-5",
            "gemini": "gemini-2.0-flash",
        }
        return defaults.get(platform, "unknown-model")
