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
    return subprocess.run(
        [sys.executable, str(SEARCH), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_success(result: subprocess.CompletedProcess, label: str) -> None:
    if result.returncode != 0:
        raise AssertionError(
            f"{label} failed with exit code {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def main() -> int:
    markdown = run(
        "oilfield operations software rugged trustworthy modern",
        "--brand-system",
        "-p",
        "FieldOps Pro",
    )
    assert_success(markdown, "Markdown brand-system command")
    required_markdown = [
        "# FieldOps Pro — Brand System",
        "## Strategic Foundation",
        "## Semantic Color Tokens",
        "## Logo Direction",
        "## Asset Creation Brief",
    ]
    for marker in required_markdown:
        if marker not in markdown.stdout:
            raise AssertionError(f"Missing Markdown marker: {marker}\n{markdown.stdout}")

    json_result = run(
        "mobile dental care trustworthy accessible compassionate",
        "--brand-system",
        "-p",
        "Assisted Dental Partners",
        "--json",
    )
    assert_success(json_result, "JSON brand-system command")
    payload = json.loads(json_result.stdout)
    for key in ["project_name", "source_query", "archetype", "personality", "logo_direction", "semantic_tokens", "asset_brief"]:
        if key not in payload:
            raise AssertionError(f"Missing JSON key: {key}")
    if payload["project_name"] != "Assisted Dental Partners":
        raise AssertionError("Project name was not preserved in JSON output")

    with tempfile.TemporaryDirectory() as temp_dir:
        persisted = run(
            "oilfield operations software rugged trustworthy modern",
            "--brand-system",
            "-p",
            "FieldOps Pro",
            "--persist",
            "--output-dir",
            temp_dir,
        )
        assert_success(persisted, "Persisted brand-system command")
        brand_dir = Path(temp_dir) / "brand-system" / "fieldops-pro"
        required_files = [
            brand_dir / "MASTER.md",
            brand_dir / "brand-system.json",
            brand_dir / "assets" / "logo-brief.md",
            brand_dir / "tokens" / "semantic-brand-tokens.json",
        ]
        for path in required_files:
            if not path.exists():
                raise AssertionError(f"Missing persisted file: {path}")
        tokens = json.loads(required_files[-1].read_text(encoding="utf-8"))
        if tokens["color"]["brand"]["primary"]["$type"] != "color":
            raise AssertionError("Semantic token output is malformed")

        skipped = run(
            "oilfield operations software rugged trustworthy modern",
            "--brand-system",
            "-p",
            "FieldOps Pro",
            "--persist",
            "--output-dir",
            temp_dir,
        )
        assert_success(skipped, "Safe persistence rerun")
        if "already exists" not in skipped.stdout:
            raise AssertionError("Existing brand system should not be silently overwritten")

        forced = run(
            "oilfield operations software rugged trustworthy modern",
            "--brand-system",
            "-p",
            "FieldOps Pro",
            "--persist",
            "--output-dir",
            temp_dir,
            "--force",
        )
        assert_success(forced, "Forced persistence rerun")

    conflict = run("test", "--brand-system", "--design-system")
    if conflict.returncode == 0:
        raise AssertionError("Mutually exclusive flags should fail")
    if "mutually exclusive" not in conflict.stderr:
        raise AssertionError(f"Expected mutual-exclusion error, got:\n{conflict.stderr}")

    invalid_persist = run("test", "--persist")
    if invalid_persist.returncode == 0 or "requires" not in invalid_persist.stderr:
        raise AssertionError("--persist without a system mode should fail")

    print("Brand system smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
