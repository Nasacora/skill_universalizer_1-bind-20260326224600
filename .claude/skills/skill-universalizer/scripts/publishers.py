"""
publishers.py — Publica variantes generadas a shared_artifacts/.
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


class SkillPublisher:
    """
    Publica las variantes generadas a shared_artifacts/universalized-skills/.
    Todas las escrituras son atómicas (temp + rename).
    """

    EXCLUDE_PATTERNS = {
        "__pycache__", ".git", ".DS_Store", ".pytest_cache",
    }
    EXCLUDE_SUFFIXES = {".pyc", ".tmp", ".bak"}

    def __init__(self):
        self.errors: list = []

    def publish(self, skill_id: str, universal: dict, variants: dict, output_root: Path, skill_path: Path = None) -> bool:
        """Publica la skill universalizada. Retorna True si OK."""
        self.errors = []
        output_root = Path(output_root)

        try:
            skill_out = output_root / skill_id
            skill_out.mkdir(parents=True, exist_ok=True)

            if skill_path:
                self._publish_universal(skill_out, skill_path, universal)

            for platform, variant in variants.items():
                self._publish_variant(platform, variant, skill_out, skill_path)

            manifest = self._build_manifest(skill_id, variants, skill_path, skill_out)
            self._atomic_write_json(skill_out / "MANIFEST.json", manifest)

            return len(self.errors) == 0

        except Exception as exc:
            self.errors.append(f"Error publicando '{skill_id}': {exc}")
            return False

    def _publish_universal(self, skill_out: Path, skill_path: Path, universal: dict) -> None:
        universal_out = skill_out / "universal"
        universal_out.mkdir(parents=True, exist_ok=True)

        core_content = universal.get("core_content", "")
        if core_content:
            self._atomic_write(universal_out / "SKILL.md", core_content)

        for subdir in ("scripts", "config"):
            src = Path(skill_path) / subdir
            if src.exists() and src.is_dir():
                self._copy_directory(src, universal_out / subdir)

    def _publish_variant(self, platform: str, variant: dict, skill_out: Path, skill_path) -> None:
        platform_out = skill_out / platform
        platform_out.mkdir(parents=True, exist_ok=True)

        content = variant.get("skill_md_content", "")
        if content:
            self._atomic_write(platform_out / "SKILL.md", content)

        if skill_path:
            scripts_src = Path(skill_path) / "scripts"
            if scripts_src.exists() and scripts_src.is_dir():
                self._copy_directory(scripts_src, platform_out / "scripts")

    def _build_manifest(self, skill_id, variants, skill_path, skill_out) -> dict:
        return {
            "skill_id": skill_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "platforms": list(variants.keys()),
            "source": str(skill_path) if skill_path else "unknown",
            "output": str(skill_out),
        }

    def _atomic_write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)

    def _atomic_write_json(self, path: Path, data: dict) -> None:
        content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        self._atomic_write(path, content)

    def _copy_directory(self, src: Path, dst: Path) -> None:
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.rglob("*"):
            if self._is_excluded(item):
                continue
            relative = item.relative_to(src)
            target = dst / relative
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif item.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)

    def _is_excluded(self, path: Path) -> bool:
        for part in path.parts:
            if part in self.EXCLUDE_PATTERNS:
                return True
        if path.suffix in self.EXCLUDE_SUFFIXES:
            return True
        return False
