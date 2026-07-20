#!/usr/bin/env python3
"""Smoke tests for the independent Brand System Extension."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEARCH = ROOT / "src" / "ui-ux-pro-max" / "scripts" / "search.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SEARCH), *args], cwd=ROOT, text=True, capture_output=True, check=False)


def assert_success(result: subprocess.CompletedProcess, label: str) -> None:
    if result.returncode != 0:
        raise AssertionError(f"{label} failed with exit code {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def main() -> int:
    markdown = run("oilfield operations software rugged trustworthy modern", "--brand-system", "-p", "FieldOps Pro")
    assert_success(markdown, "Markdown brand-system command")
    for marker in ["# FieldOps Pro — Brand System", "## Strategic Foundation", "## Semantic Color Tokens", "## Logo Direction"]:
        if marker not in markdown.stdout:
            raise AssertionError(f"Missing Markdown marker: {marker}")

    json_result = run("mobile dental care trustworthy accessible compassionate", "--brand-system", "-p", "Assisted Dental Partners", "--json")
    assert_success(json_result, "JSON brand-system command")
    payload = json.loads(json_result.stdout)
    for key in ["project_name", "source_query", "archetype", "personality", "logo_direction", "semantic_tokens", "asset_brief"]:
        if key not in payload:
            raise AssertionError(f"Missing JSON key: {key}")

    with tempfile.TemporaryDirectory() as temp_dir:
        persisted = run(
            "oilfield operations software rugged trustworthy modern", "--brand-system", "-p", "FieldOps Pro",
            "--persist", "--generate-assets", "--presentation-system", "--deck-type", "executive",
            "--export-tokens", "--token-formats", "css,tailwind,typescript", "--output-dir", temp_dir,
        )
        assert_success(persisted, "Persisted brand system with token exports")
        brand_dir = Path(temp_dir) / "brand-system" / "fieldops-pro"
        required_files = [
            brand_dir / "MASTER.md",
            brand_dir / "tokens" / "semantic-brand-tokens.json",
            brand_dir / "assets" / "generation-prompts.json",
            brand_dir / "exports" / "svg" / "emblem-template.svg",
            brand_dir / "presentations" / "PRESENTATION-SYSTEM.md",
            brand_dir / "exports" / "css" / "brand-tokens.css",
            brand_dir / "exports" / "tailwind" / "brand-theme.js",
            brand_dir / "exports" / "typescript" / "brand-tokens.ts",
            brand_dir / "exports" / "json" / "semantic-brand-tokens.json",
        ]
        for path in required_files:
            if not path.exists():
                raise AssertionError(f"Missing persisted file: {path}")

        source = json.loads((brand_dir / "tokens" / "semantic-brand-tokens.json").read_text(encoding="utf-8"))
        exported = json.loads((brand_dir / "exports" / "json" / "semantic-brand-tokens.json").read_text(encoding="utf-8"))
        if source != exported:
            raise AssertionError("Exported JSON tokens do not match the semantic source of truth")
        primary = source["color"]["brand"]["primary"]["$value"]
        accent = source["color"]["brand"]["accent"]["$value"]
        css = (brand_dir / "exports" / "css" / "brand-tokens.css").read_text(encoding="utf-8")
        tailwind = (brand_dir / "exports" / "tailwind" / "brand-theme.js").read_text(encoding="utf-8")
        typescript = (brand_dir / "exports" / "typescript" / "brand-tokens.ts").read_text(encoding="utf-8")
        for label, content in [("CSS", css), ("Tailwind", tailwind), ("TypeScript", typescript)]:
            if primary not in content or accent not in content:
                raise AssertionError(f"{label} export is not aligned with source tokens")
        if '[data-theme="dark"]' not in css or "as const" not in typescript or "theme" not in tailwind:
            raise AssertionError("Production export structure is malformed")

    invalid_cases = [
        (("test", "--persist"), "requires"),
        (("test", "--brand-system", "--generate-assets"), "requires --brand-system --persist"),
        (("test", "--brand-system", "--presentation-system"), "requires --brand-system --persist"),
        (("test", "--brand-system", "--export-tokens"), "requires --brand-system --persist"),
        (("test", "--brand-system", "--persist", "--token-formats", "css,banana"), "unsupported token format"),
    ]
    for args, expected in invalid_cases:
        result = run(*args)
        if result.returncode == 0 or expected not in result.stderr:
            raise AssertionError(f"Expected CLI error containing {expected!r}: {result.stderr}")

    conflict = run("test", "--brand-system", "--design-system")
    if conflict.returncode == 0 or "mutually exclusive" not in conflict.stderr:
        raise AssertionError("Mutually exclusive flags should fail")

    print("Brand system smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
