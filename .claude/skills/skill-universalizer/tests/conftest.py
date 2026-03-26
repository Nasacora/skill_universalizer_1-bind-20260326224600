"""
conftest.py — Fixtures compartidas para todos los tests.
"""
import pytest


@pytest.fixture
def minimal_skill(tmp_path):
    """Skill mínima válida para tests."""
    content = "# Test Skill\n\nContenido de la skill de prueba.\n\nMás contenido aquí.\n" * 3
    (tmp_path / "SKILL.md").write_text(content, encoding="utf-8")

    providers_dir = tmp_path / "providers"
    providers_dir.mkdir()
    (providers_dir / "claude.yml").write_text(
        "trigger: cuando hay que probar\nmodel: claude-haiku-4-5\nhooks:\n  - stop\n",
        encoding="utf-8",
    )

    (tmp_path / "skill.yaml").write_text(
        "id: test-skill\nname: Test Skill\ndescription: Skill de test para el universalizador\n"
        "purpose: Probar el motor\nkeywords:\n  - test\n  - universalizer\nstatus: active\n"
        "visibility: public\nwhen_to_use: Cuando se necesita probar\nagent: null\n"
        "platforms:\n  - claude\ncore: SKILL.md\nproviders:\n  claude:\n"
        "    frontmatter: providers/claude.yml\nversion: \"1.0.0\"\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def skill_with_scripts(minimal_skill):
    """Skill mínima con directorio scripts/."""
    scripts_dir = minimal_skill / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run.py").write_text("# script de prueba\nprint('hello')\n", encoding="utf-8")
    (scripts_dir / "_platform_config.py").write_text(
        "def detect_platform(): return 'claude'\n", encoding="utf-8"
    )
    return minimal_skill


@pytest.fixture
def skill_with_codex_provider(minimal_skill):
    """Skill con proveedor codex además de claude."""
    (minimal_skill / "providers" / "codex.yml").write_text(
        "trigger: when code needs testing\nmodel: gpt-4o\nhooks: []\nnotes: no hooks\n",
        encoding="utf-8",
    )
    skill_yaml = minimal_skill / "skill.yaml"
    content = skill_yaml.read_text(encoding="utf-8")
    content = content.replace(
        "  claude:\n    frontmatter: providers/claude.yml",
        "  claude:\n    frontmatter: providers/claude.yml\n  codex:\n    frontmatter: providers/codex.yml",
    )
    content = content.replace(
        "platforms:\n  - claude",
        "platforms:\n  - claude\n  - codex",
    )
    skill_yaml.write_text(content, encoding="utf-8")
    return minimal_skill
