# Skill-Universalizer

Motor Python CLI que transforma skills específicas de una plataforma de IA
en variantes universales para múltiples plataformas.

## Instalación

```bash
pip3 install pyyaml jinja2 pytest
```

## Uso rápido

```bash
cd .claude/skills/skill-universalizer

# Validar (sin escribir)
python3 scripts/universalize.py \
  --skill ../docs-sync \
  --target-platforms codex,cursor \
  --validate-only

# Publicar
python3 scripts/universalize.py \
  --skill ../docs-sync \
  --target-platforms codex,cursor
```

## Tests

```bash
cd .claude/skills/skill-universalizer
python3 -m pytest tests/ -v
```

## Estructura del proyecto

```
.claude/skills/
├── skill-universalizer/
│   ├── SKILL.md
│   ├── skill.yaml
│   ├── scripts/
│   │   ├── universalize.py        ← CLI principal
│   │   ├── skill_analyzer.py
│   │   ├── universal_extractor.py
│   │   ├── variant_generator.py
│   │   ├── validator.py
│   │   ├── publishers.py
│   │   └── _platform_config.py
│   ├── templates/
│   │   ├── SKILL_BASE.md.j2
│   │   ├── SKILL_CLAUDE.md.j2
│   │   ├── SKILL_CODEX.md.j2
│   │   └── SKILL_CURSOR.md.j2
│   ├── config/
│   │   ├── universalization.yaml
│   │   └── platform-profiles.yaml
│   ├── tests/
│   └── docs/
└── docs-sync/                     ← Skill de ejemplo
    ├── skill.yaml
    ├── SKILL.md
    └── providers/
```
