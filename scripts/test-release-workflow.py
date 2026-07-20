#!/usr/bin/env python3
"""End-to-end smoke test for the complete brand package workflow."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEARCH = ROOT / "src" / "ui-ux-pro-max" / "scripts" / "search.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SEARCH), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        result = run(
            "oilfield operations software rugged trustworthy modern",
            "--complete-brand-package",
            "--deck-type",
            "executive",
            "-p",
            "FieldOps Pro",
            "--output-dir",
            temp_dir,
            "--json",
        )
        if result.returncode != 0:
            raise AssertionError(f"Complete package failed:\n{result.stdout}\n{result.stderr}")

        payload = json.loads(result.stdout)
        for key in ["brand_system", "persistence", "asset_generation", "presentation_generation", "token_exports"]:
            if not payload.get(key):
                raise AssertionError(f"Missing complete-package payload: {key}")

        brand_dir = Path(temp_dir) / "brand-system" / "fieldops-pro"
        required = [
            brand_dir / "MASTER.md",
            brand_dir / "assets" / "generation-prompts.json",
            brand_dir / "presentations" / "executive-deck-outline.md",
            brand_dir / "exports" / "css" / "brand-tokens.css",
            brand_dir / "exports" / "tailwind" / "brand-theme.js",
            brand_dir / "exports" / "typescript" / "brand-tokens.ts",
            brand_dir / "exports" / "json" / "semantic-brand-tokens.json",
        ]
        for path in required:
            if not path.exists():
                raise AssertionError(f"Missing complete-package file: {path}")

        rerun = run(
            "oilfield operations software rugged trustworthy modern",
            "--complete-brand-package",
            "-p",
            "FieldOps Pro",
            "--output-dir",
            temp_dir,
        )
        if rerun.returncode != 0 or "already exists" not in rerun.stdout:
            raise AssertionError("Complete package must preserve safe no-overwrite behavior")

    print("Release workflow smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
