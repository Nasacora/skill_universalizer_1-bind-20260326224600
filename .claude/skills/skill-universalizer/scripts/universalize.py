"""
universalize.py — Orquestador CLI del skill-universalizer.

Uso:
    python3 scripts/universalize.py \
        --skill /ruta/a/mi-skill \
        --target-platforms codex,cursor \
        --output shared_artifacts/universalized-skills
"""
import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from skill_analyzer import SkillAnalyzer
from universal_extractor import UniversalExtractor
from variant_generator import VariantGenerator
from validator import SkillValidator
from publishers import SkillPublisher


def _ok(msg: str) -> None:
    print(f"  \033[32m✓\033[0m {msg}")


def _err(msg: str) -> None:
    print(f"  \033[31m✗\033[0m {msg}", file=sys.stderr)


def _info(msg: str) -> None:
    print(f"  → {msg}")


def _header(step: int, total: int, label: str) -> None:
    print(f"\n\033[1m[{step}/{total}] {label}...\033[0m")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="universalize",
        description="Transforma una skill específica en universal multi-plataforma.",
    )
    parser.add_argument("--skill", required=True, type=Path)
    parser.add_argument("--target-platforms", required=True, type=str)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--validate-only", action="store_true", default=False)
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--verbose", action="store_true", default=False)
    return parser.parse_args()


def _resolve_output_root(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output.resolve()
    skill_path = args.skill.resolve()
    for parent in [skill_path] + list(skill_path.parents):
        if (parent / ".claude").exists() or (parent / ".git").exists():
            return parent / "shared_artifacts" / "universalized-skills"
    return Path.cwd() / "shared_artifacts" / "universalized-skills"


def main() -> int:
    args = _parse_args()
    skill_path = args.skill.resolve()
    target_platforms = [p.strip() for p in args.target_platforms.split(",") if p.strip()]
    output_root = _resolve_output_root(args)
    total_steps = 4 if args.validate_only else 5

    print(
        f"\n\033[1m[universalize]\033[0m Iniciando: "
        f"{skill_path.name} → {', '.join(target_platforms)}"
    )
    if args.dry_run:
        print("  \033[33m⚠ Modo dry-run: no se escribirá nada\033[0m")

    _header(1, total_steps, "Analizando estructura")
    analyzer = SkillAnalyzer()
    analyzer.analyze(skill_path)

    if not analyzer.is_valid():
        for e in analyzer.errors:
            _err(e)
        return 1

    _ok(f"skill_id: {analyzer.skill_id}")
    _ok(f"Plataformas actuales: {', '.join(analyzer.current_platforms) or 'ninguna'}")

    if args.verbose:
        _info(f"core: {analyzer.metadata.get('core')}")
        _info(f"providers declarados: {list(analyzer.metadata.get('providers', {}).keys())}")

    _header(2, total_steps, "Extrayendo contenido universal")
    extractor = UniversalExtractor()
    universal = extractor.extract(skill_path, analyzer.metadata)

    if universal is None:
        _err(extractor.last_error)
        return 1

    core_lines = len(universal["core_content"].splitlines())
    _ok(f"core: {analyzer.metadata.get('core')} ({core_lines} líneas)")

    _header(3, total_steps, "Generando variantes")
    generator = VariantGenerator(skill_path=skill_path)
    variants: dict = {}

    for platform in target_platforms:
        sys.stdout.write(f"  → {platform}...")
        sys.stdout.flush()
        variant = generator.generate(
            analyzer.skill_id, universal, analyzer.metadata, platform, skill_path
        )
        if variant is None:
            print(f" \033[31m✗\033[0m")
            _err(generator.last_error)
            return 1
        variants[platform] = variant
        print(f" \033[32m✓\033[0m")

    _header(4, total_steps, "Validando")
    validator = SkillValidator()
    all_valid = True

    for platform, variant in variants.items():
        ok = validator.validate(variant, platform)
        if ok:
            _ok(f"{platform}: válido")
        else:
            _err(f"{platform}: inválido")
            for e in validator.errors:
                _err(f"  {e}")
            all_valid = False

    if not all_valid:
        return 1

    if args.validate_only:
        print(f"\n\033[32m✅ Validación completada.\033[0m {len(variants)} variante(s) válidas.")
        return 0

    _header(5, total_steps, "Publicando")

    if args.dry_run:
        _info(f"(dry-run) output: {output_root / analyzer.skill_id}")
        for platform in variants:
            _ok(f"(dry-run) {platform}/SKILL.md")
        print(f"\n\033[32m✅ Dry-run completado.\033[0m {len(variants)} variante(s).")
        return 0

    publisher = SkillPublisher()
    success = publisher.publish(
        analyzer.skill_id, universal, variants, output_root, skill_path
    )

    if not success:
        for e in publisher.errors:
            _err(e)
        return 1

    _ok(f"{output_root / analyzer.skill_id}/")
    print(f"\n\033[32m✅ Completado.\033[0m {len(variants)} variante(s) generada(s).\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
