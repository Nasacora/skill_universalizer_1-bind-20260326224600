"""
test_publishers.py — Tests para SkillPublisher.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
import yaml
from publishers import SkillPublisher
from universal_extractor import UniversalExtractor
from variant_generator import VariantGenerator


def _load_meta(skill_path: Path) -> dict:
    with open(skill_path / "skill.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_variants(skill_path: Path, platforms: list) -> dict:
    meta = _load_meta(skill_path)
    extractor = UniversalExtractor()
    universal = extractor.extract(skill_path, meta)
    gen = VariantGenerator(skill_path=skill_path)
    variants = {}
    for p in platforms:
        v = gen.generate("test-skill", universal, meta, p, skill_path)
        if v:
            variants[p] = v
    return variants


class TestSkillPublisherStructure:
    def test_creates_output_directory(self, minimal_skill, tmp_path):
        publisher = SkillPublisher()
        meta = _load_meta(minimal_skill)
        extractor = UniversalExtractor()
        universal = extractor.extract(minimal_skill, meta)
        variants = _build_variants(minimal_skill, ["claude"])
        output_root = tmp_path / "output"
        result = publisher.publish("test-skill", universal, variants, output_root, minimal_skill)
        assert result is True, f"Errores: {publisher.errors}"
        assert (output_root / "test-skill").is_dir()

    def test_creates_universal_directory(self, minimal_skill, tmp_path):
        publisher = SkillPublisher()
        meta = _load_meta(minimal_skill)
        extractor = UniversalExtractor()
        universal = extractor.extract(minimal_skill, meta)
        variants = _build_variants(minimal_skill, ["claude"])
        output_root = tmp_path / "output"
        publisher.publish("test-skill", universal, variants, output_root, minimal_skill)
        assert (output_root / "test-skill" / "universal").is_dir()

    def test_creates_skill_md_in_platform_dir(self, minimal_skill, tmp_path):
        publisher = SkillPublisher()
        meta = _load_meta(minimal_skill)
        extractor = UniversalExtractor()
        universal = extractor.extract(minimal_skill, meta)
        variants = _build_variants(minimal_skill, ["claude"])
        output_root = tmp_path / "output"
        publisher.publish("test-skill", universal, variants, output_root, minimal_skill)
        skill_md = output_root / "test-skill" / "claude" / "SKILL.md"
        assert skill_md.exists()
        assert skill_md.stat().st_size > 0


class TestSkillPublisherManifest:
    def test_manifest_is_created(self, minimal_skill, tmp_path):
        publisher = SkillPublisher()
        meta = _load_meta(minimal_skill)
        extractor = UniversalExtractor()
        universal = extractor.extract(minimal_skill, meta)
        variants = _build_variants(minimal_skill, ["claude"])
        output_root = tmp_path / "output"
        publisher.publish("test-skill", universal, variants, output_root, minimal_skill)
        assert (output_root / "test-skill" / "MANIFEST.json").exists()

    def test_manifest_is_valid_json(self, minimal_skill, tmp_path):
        publisher = SkillPublisher()
        meta = _load_meta(minimal_skill)
        extractor = UniversalExtractor()
        universal = extractor.extract(minimal_skill, meta)
        variants = _build_variants(minimal_skill, ["claude"])
        output_root = tmp_path / "output"
        publisher.publish("test-skill", universal, variants, output_root, minimal_skill)
        with open(output_root / "test-skill" / "MANIFEST.json") as f:
            manifest = json.load(f)
        assert manifest["skill_id"] == "test-skill"
        assert "claude" in manifest["platforms"]


class TestSkillPublisherIdempotent:
    def test_idempotent_double_run(self, minimal_skill, tmp_path):
        publisher = SkillPublisher()
        meta = _load_meta(minimal_skill)
        extractor = UniversalExtractor()
        universal = extractor.extract(minimal_skill, meta)
        variants = _build_variants(minimal_skill, ["claude"])
        output_root = tmp_path / "output"
        r1 = publisher.publish("test-skill", universal, variants, output_root, minimal_skill)
        r2 = publisher.publish("test-skill", universal, variants, output_root, minimal_skill)
        assert r1 is True
        assert r2 is True
