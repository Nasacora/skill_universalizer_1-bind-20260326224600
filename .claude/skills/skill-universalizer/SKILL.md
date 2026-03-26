# skill-universalizer

Transforma una skill diseñada para una plataforma de IA en variantes universales
que funcionan en múltiples plataformas simultáneamente, sin duplicar código.

**Una fuente de verdad → múltiples plataformas generadas automáticamente.**

---

## Cuándo usar

Cuando tienes una skill funcionando en Claude y quieres portarla a Codex, Cursor
o Gemini sin copiar ni mantener archivos duplicados.

---

## Requisitos previos

La skill a universalizar **debe tener**:

1. `skill.yaml` en su raíz (metadatos universales)
2. Archivo core indicado en `skill.yaml.core` (ej: `SKILL.md`)
3. Al menos un `providers/PLATFORM.yml` por plataforma ya soportada

---

## Uso

```bash
python3 scripts/universalize.py \
  --skill /ruta/a/mi-skill \
  --target-platforms codex,cursor \
  --output shared_artifacts/universalized-skills
```

### Argumentos

| Argumento | Requerido | Descripción |
|-----------|-----------|-------------|
| `--skill PATH` | ✅ | Ruta a la skill a universalizar |
| `--target-platforms` | ✅ | Plataformas destino (comma-separated) |
| `--output PATH` | ❌ | Output dir |
| `--validate-only` | ❌ | Solo validar, no publicar |
| `--dry-run` | ❌ | Simular sin escribir nada |
| `--verbose` | ❌ | Output detallado |

### Plataformas soportadas

`claude` · `codex` · `cursor` · `gemini`

---

## Tests

```bash
cd .claude/skills/skill-universalizer
python3 -m pytest tests/ -v
```
