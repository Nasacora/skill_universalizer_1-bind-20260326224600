"""
test_extractor.py — Tests para UniversalExtractor.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
import yaml
from universal_extractor import UniversalExtractor


def _get_metadata(skill_path: Path) -> dict:
    with open(skill_path / "skill.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestUniversalExtractorValid:
    def test_extracts_skill_id(self, minimal_skill):
        extractor = UniversalExtractor()
        meta = _get_metadata(minimal_skill)
        result = extractor.extract(minimal_skill, meta)
        assert result is not None
        assert result["skill_id"] == "test-skill"

    def test_extracts_core_content(self, minimal_skill):
        extractor = UniversalExtractor()
        meta = _get_metadata(minimal_skill)
        result = extractor.extract(minimal_skill, meta)
        assert result is not None
        assert "Test Skill" in result["core_content"]

    def test_extracts_name_and_description(self, minimal_skill):
        extractor = UniversalExtractor()
        meta = _get_metadata(minimal_skill)
        result = extractor.extract(minimal_skill, meta)
        assert result["name"] == "Test Skill"
        assert result["description"] == "Skill de test para el universalizador"

    def test_extracts_scripts(self, skill_with_scripts):
        extractor = UniversalExtractor()
        with open(skill_with_scripts / "skill.yaml", encoding="utf-8") as f:
            meta = yaml.safe_load(f)
        result = extractor.extract(skill_with_scripts, meta)
        assert result is not None
        assert len(result["scripts"]) >= 1

    def test_has_tests_false(self, minimal_skill):
        extractor = UniversalExtractor()
        meta = _get_metadata(minimal_skill)
        result = extractor.extract(minimal_skill, meta)
        assert result["has_tests"] is False

    def test_has_tests_true(self, minimal_skill):
        (minimal_skill / "tests").mkdir()
        extractor = UniversalExtractor()
        meta = _get_metadata(minimal_skill)
        result = extractor.extract(minimal_skill, meta)
        assert result["has_tests"] is True

    def test_keywords_extracted(self, minimal_skill):
        extractor = UniversalExtractor()
        meta = _get_metadata(minimal_skill)
        result = extractor.extract(minimal_skill, meta)
        assert "test" in result["keywords"]

    def test_version_extracted(self, minimal_skill):
        extractor = UniversalExtractor()
        meta = _get_metadata(minimal_skill)
        result = extractor.extract(minimal_skill, meta)
        assert result["version"] == "1.0.0"


class TestUniversalExtractorFailure:
    def test_returns_none_when_core_missing(self, tmp_path):
        (tmp_path / "providers").mkdir()
        (tmp_path / "providers" / "claude.yml").write_text("trigger: t")
        (tmp_path / "skill.yaml").write_text(
            "id: x-skill\nname: X\ncore: NONEXISTENT.md\nproviders:\n  claude:\n    frontmatter: providers/claude.yml\n"
        )
        with open(tmp_path / "skill.yaml") as f:
            meta = yaml.safe_load(f)
        extractor = UniversalExtractor()
        result = extractor.extract(tmp_path, meta)
        assert result is None

    def test_last_error_populated_on_failure(self, tmp_path):
        (tmp_path / "skill.yaml").write_text(
            "id: x-skill\nname: X\ncore: MISSING.md\nproviders:\n  claude:\n    frontmatter: providers/claude.yml\n"
        )
        with open(tmp_path / "skill.yaml") as f:
            meta = yaml.safe_load(f)
        extractor = UniversalExtractor()
        extractor.extract(tmp_path, meta)
        assert extractor.last_error != ""
