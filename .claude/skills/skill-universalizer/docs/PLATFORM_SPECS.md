# PLATFORM_SPECS

> Especificaciones de cada plataforma soportada.

## Claude Code — `.claude/skills/`
- Hooks: stop, pre_tool_use, post_tool_use
- Modelos: claude-haiku-4-5, claude-sonnet-4-5, claude-opus-4-5

## Codex CLI — `.codex/skills/`
- Sin hooks nativos
- Modelos: gpt-4o, gpt-4-turbo

## Cursor — `.cursor/rules/`
- Sin hooks nativos, formato .mdc
- Modelos: claude-sonnet-4-5, gpt-4o

## Gemini CLI — `.gemini/skills/`
- Sin hooks, contexto largo (1M tokens)
- Modelos: gemini-2.0-flash, gemini-1.5-pro
