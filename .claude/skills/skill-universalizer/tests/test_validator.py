"""
test_validator.py — Tests para SkillValidator.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from datetime import datetime, timezone
import pytest
from validator import SkillValidator


def _make_valid_variant(platform: str = "claude") -> dict:
    content = "\n".join([
        "# Test Skill",
        "",
        "Descripción de la skill.",
        "",
        "## Cuándo usar",
        "",
        "Cuando necesitas probar.",
        "",
        "## Contenido",
        "",
        "Contenido universal de la skill.",
        "Más detalles aquí.",
        "",
        "---",
        "*Generado automáticamente.*",
    ])
    return {
        "skill_id": "test-skill",
        "platform": platform,
        "skill_md_content": content,
        "provider_meta": {"trigger": "test", "model": "claude-haiku-4-5"},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


class TestSkillValidatorValid:
    def test_valid_variant_passes(self):
        validator = SkillValidator()
        assert validator.validate(_make_valid_variant("claude"), "claude") is True
        assert validator.errors == []

    def test_valid_codex_variant(self):
        validator = SkillValidator()
        assert validator.validate(_make_valid_variant("codex"), "codex") is True

    def test_valid_cursor_variant(self):
        validator = SkillValidator()
        assert validator.validate(_make_valid_variant("cursor"), "cursor") is True


class TestSkillValidatorInvalid:
    def test_missing_skill_id(self):
        validator = SkillValidator()
        variant = _make_valid_variant()
        del variant["skill_id"]
        assert validator.validate(variant, "claude") is False
        assert any("skill_id" in e for e in validator.errors)

    def test_invalid_skill_id_uppercase(self):
        validator = SkillValidator()
        variant = _make_valid_variant()
        variant["skill_id"] = "Test-Skill"
        assert validator.validate(variant, "claude") is False
        assert any("kebab-case" in e for e in validator.errors)

    def test_unknown_platform(self):
        validator = SkillValidator()
        assert validator.validate(_make_valid_variant(), "unknownplatform") is False

    def test_empty_content(self):
        validator = SkillValidator()
        variant = _make_valid_variant()
        variant["skill_md_content"] = ""
        assert validator.validate(variant, "claude") is False

    def test_absolute_path_linux(self):
        validator = SkillValidator()
        variant = _make_valid_variant()
        variant["skill_md_content"] += "\nRuta: /home/user/project/skill.md\n"
        assert validator.validate(variant, "claude") is False

    def test_too_few_lines(self):
        validator = SkillValidator()
        variant = _make_valid_variant()
        variant["skill_md_content"] = "# Skill\nLinea 2\nLinea 3\n"
        assert validator.validate(variant, "claude") is False

    def test_invalid_generated_at(self):
        validator = SkillValidator()
        variant = _make_valid_variant()
        variant["generated_at"] = "not-a-timestamp"
        assert validator.validate(variant, "claude") is False

    def test_not_a_dict(self):
        validator = SkillValidator()
        assert validator.validate("not a dict", "claude") is False
