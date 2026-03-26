"""
test_generator.py — Tests para VariantGenerator.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
import yaml
from variant_generator import VariantGenerator
from universal_extractor import UniversalExtractor


def _load_meta(skill_path: Path) -> dict:
    with open(skill_path / "skill.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_universal(skill_path: Path) -> dict:
    meta = _load_meta(skill_path)
    extractor = UniversalExtractor()
    return extractor.extract(skill_path, meta)


class TestVariantGeneratorValid:
    def test_generates_for_claude(self, minimal_skill):
        meta = _load_meta(minimal_skill)
        universal = _get_universal(minimal_skill)
        gen = VariantGenerator(skill_path=minimal_skill)
        result = gen.generate("test-skill", universal, meta, "claude", minimal_skill)
        assert result is not None, f"Error: {gen.last_error}"
        assert result["platform"] == "claude"
        assert result["skill_id"] == "test-skill"

    def test_generated_content_not_empty(self, minimal_skill):
        meta = _load_meta(minimal_skill)
        universal = _get_universal(minimal_skill)
        gen = VariantGenerator(skill_path=minimal_skill)
        result = gen.generate("test-skill", universal, meta, "claude", minimal_skill)
        assert result["skill_md_content"].strip() != ""

    def test_generates_for_codex_with_provider(self, skill_with_codex_provider):
        meta = _load_meta(skill_with_codex_provider)
        universal = _get_universal(skill_with_codex_provider)
        gen = VariantGenerator(skill_path=skill_with_codex_provider)
        result = gen.generate("test-skill", universal, meta, "codex", skill_with_codex_provider)
        assert result is not None, f"Error: {gen.last_error}"
        assert result["platform"] == "codex"

    def test_generates_for_cursor_without_provider(self, minimal_skill):
        meta = _load_meta(minimal_skill)
        universal = _get_universal(minimal_skill)
        gen = VariantGenerator(skill_path=minimal_skill)
        result = gen.generate("test-skill", universal, meta, "cursor", minimal_skill)
        assert result is not None, f"Error: {gen.last_error}"

    def test_generated_at_present(self, minimal_skill):
        meta = _load_meta(minimal_skill)
        universal = _get_universal(minimal_skill)
        gen = VariantGenerator(skill_path=minimal_skill)
        result = gen.generate("test-skill", universal, meta, "claude", minimal_skill)
        assert "generated_at" in result
        assert result["generated_at"] != ""


class TestVariantGeneratorInvalid:
    def test_returns_none_for_unknown_platform(self, minimal_skill):
        meta = _load_meta(minimal_skill)
        universal = _get_universal(minimal_skill)
        gen = VariantGenerator(skill_path=minimal_skill)
        result = gen.generate("test-skill", universal, meta, "unknownplatform", minimal_skill)
        assert result is None

    def test_last_error_on_unknown_platform(self, minimal_skill):
        meta = _load_meta(minimal_skill)
        universal = _get_universal(minimal_skill)
        gen = VariantGenerator(skill_path=minimal_skill)
        gen.generate("test-skill", universal, meta, "notaplatform", minimal_skill)
        assert gen.last_error != ""

    def test_returns_none_when_no_skill_path(self, minimal_skill):
        meta = _load_meta(minimal_skill)
        universal = _get_universal(minimal_skill)
        gen = VariantGenerator()
        result = gen.generate("test-skill", universal, meta, "claude")
        assert result is None
