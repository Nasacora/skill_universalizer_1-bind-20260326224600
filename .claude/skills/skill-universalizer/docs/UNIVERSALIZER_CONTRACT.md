# UNIVERSALIZER_CONTRACT

> Especificación pública del contrato que debe cumplir una skill
> para ser universalizable por skill-universalizer.

---

## 1. Estructura obligatoria

```
mi-skill/
├── skill.yaml                 ← OBLIGATORIO
├── SKILL.md                   ← OBLIGATORIO
└── providers/
    └── PLATFORM.yml           ← AL MENOS UNO
```

---

## 2. skill.yaml — Campos obligatorios

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único. **Debe ser kebab-case** (`^[a-z][a-z0-9-]+$`) |
| `name` | string | Nombre legible |
| `core` | string | Ruta relativa al archivo core (ej: `SKILL.md`) |
| `providers` | map | Al menos un provider declarado |

### Campos opcionales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `description` | string | Descripción corta |
| `status` | string | `active` \| `beta` \| `deprecated` \| `hidden` |
| `visibility` | string | `public` \| `private` \| `internal` |
| `when_to_use` | string | Cuándo invocar esta skill |
| `agent` | string \| null | Nombre del agente asociado o `null` |
| `platforms` | list | Plataformas actuales |
| `version` | string | Semver (ej: `"1.0.0"`) |

---

## 3. providers/PLATFORM.yml

Solo incluir lo diferente por plataforma:

```yaml
trigger: "texto que activa la skill"
model: claude-haiku-4-5
hooks:
  - stop
notes: ""
```

---

## 4. Plataformas soportadas

| Plataforma | Skill dir | Hooks |
|------------|-----------|-------|
| `claude` | `.claude/skills/` | ✅ |
| `codex` | `.codex/skills/` | ❌ |
| `cursor` | `.cursor/rules/` | ❌ |
| `gemini` | `.gemini/skills/` | ❌ |
