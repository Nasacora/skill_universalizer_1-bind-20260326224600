"""
test_analyzer.py — Tests para SkillAnalyzer.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
from skill_analyzer import SkillAnalyzer


class TestSkillAnalyzerValid:
    def test_valid_minimal_skill(self, minimal_skill):
        analyzer = SkillAnalyzer()
        analyzer.analyze(minimal_skill)
        assert analyzer.is_valid(), f"Esperaba válida, errores: {analyzer.errors}"
        assert analyzer.skill_id == "test-skill"

    def test_extracts_metadata(self, minimal_skill):
        analyzer = SkillAnalyzer()
        analyzer.analyze(minimal_skill)
        assert analyzer.metadata["name"] == "Test Skill"

    def test_extracts_current_platforms(self, minimal_skill):
        analyzer = SkillAnalyzer()
        analyzer.analyze(minimal_skill)
        assert "claude" in analyzer.current_platforms

    def test_valid_with_multiple_providers(self, skill_with_codex_provider):
        analyzer = SkillAnalyzer()
        analyzer.analyze(skill_with_codex_provider)
        assert analyzer.is_valid(), f"Errores: {analyzer.errors}"


class TestSkillAnalyzerInvalid:
    def test_missing_directory(self, tmp_path):
        analyzer = SkillAnalyzer()
        analyzer.analyze(tmp_path / "no-existe")
        assert not analyzer.is_valid()
        assert any("no existe" in e for e in analyzer.errors)

    def test_missing_skill_yaml(self, tmp_path):
        analyzer = SkillAnalyzer()
        analyzer.analyze(tmp_path)
        assert not analyzer.is_valid()
        assert any("skill.yaml" in e for e in analyzer.errors)

    def test_invalid_yaml_syntax(self, tmp_path):
        (tmp_path / "skill.yaml").write_text("id: [\nbad yaml{{", encoding="utf-8")
        analyzer = SkillAnalyzer()
        analyzer.analyze(tmp_path)
        assert not analyzer.is_valid()
        assert any("YAML" in e for e in analyzer.errors)

    def test_missing_required_field_id(self, tmp_path):
        (tmp_path / "SKILL.md").write_text("# skill")
        (tmp_path / "providers").mkdir()
        (tmp_path / "providers" / "claude.yml").write_text("trigger: test")
        (tmp_path / "skill.yaml").write_text(
            "name: Test\ncore: SKILL.md\nproviders:\n  claude:\n    frontmatter: providers/claude.yml\n"
        )
        analyzer = SkillAnalyzer()
        analyzer.analyze(tmp_path)
        assert not analyzer.is_valid()
        assert any("'id'" in e for e in analyzer.errors)

    def test_invalid_id_uppercase(self, tmp_path):
        (tmp_path / "SKILL.md").write_text("# skill")
        (tmp_path / "providers").mkdir()
        (tmp_path / "providers" / "claude.yml").write_text("trigger: test")
        (tmp_path / "skill.yaml").write_text(
            "id: Test-Skill\nname: Test\ncore: SKILL.md\nproviders:\n  claude:\n    frontmatter: providers/claude.yml\n"
        )
        analyzer = SkillAnalyzer()
        analyzer.analyze(tmp_path)
        assert not analyzer.is_valid()
        assert any("kebab-case" in e for e in analyzer.errors)

    def test_provider_file_missing(self, tmp_path):
        (tmp_path / "SKILL.md").write_text("# skill")
        (tmp_path / "providers").mkdir()
        (tmp_path / "skill.yaml").write_text(
            "id: test-skill\nname: Test\ncore: SKILL.md\nproviders:\n  claude:\n    frontmatter: providers/claude.yml\n"
        )
        analyzer = SkillAnalyzer()
        analyzer.analyze(tmp_path)
        assert not analyzer.is_valid()
        assert any("claude" in e for e in analyzer.errors)

    def test_empty_providers(self, tmp_path):
        (tmp_path / "SKILL.md").write_text("# skill")
        (tmp_path / "skill.yaml").write_text(
            "id: test-skill\nname: Test\ncore: SKILL.md\nproviders: {}\n"
        )
        analyzer = SkillAnalyzer()
        analyzer.analyze(tmp_path)
        assert not analyzer.is_valid()
