# EXAMPLES

## Universalizar docs-sync a Codex

```bash
# 1. Validar primero
python3 .claude/skills/skill-universalizer/scripts/universalize.py \
  --skill .claude/skills/docs-sync \
  --target-platforms codex \
  --validate-only --verbose

# 2. Publicar
python3 .claude/skills/skill-universalizer/scripts/universalize.py \
  --skill .claude/skills/docs-sync \
  --target-platforms codex,cursor
```

## Múltiples plataformas

```bash
python3 .claude/skills/skill-universalizer/scripts/universalize.py \
  --skill .claude/skills/docs-sync \
  --target-platforms codex,cursor,gemini \
  --verbose
```

## Dry-run (simular sin escribir)

```bash
python3 .claude/skills/skill-universalizer/scripts/universalize.py \
  --skill .claude/skills/docs-sync \
  --target-platforms codex \
  --dry-run
```
