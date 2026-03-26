# docs-sync

Universal documentation synchronization pipeline.
Keeps project documentation in sync with the actual state of the system.

## Purpose

Automate the process of updating project documentation to reflect the
current state of the codebase, metrics, and system configuration.

## Features

- Scan project structure and detect documentation drift
- Update README files and architecture docs
- Synchronize metrics and status badges
- Generate changelog entries from commit history
- Validate cross-references between docs

## How it works

1. Reads the current project structure
2. Compares with existing documentation
3. Identifies outdated sections
4. Updates documentation files
5. Reports changes made

## Usage

Invoke this skill when:
- After significant code changes
- Before releases or milestones
- When documentation feels stale

## Configuration

The pipeline reads from `config/pipeline.json` if present:

```json
{
  "scan_dirs": ["src", "lib", "scripts"],
  "doc_dirs": ["docs", "README.md"],
  "exclude": ["node_modules", ".git", "__pycache__"]
}
```

## Output

- Updated markdown files in `docs/`
- Summary report of changes made
- List of files modified

## Notes

- Non-destructive: creates backups before modifying
- Idempotent: running twice produces the same result
- Platform-agnostic: works in Claude, Codex, Cursor
