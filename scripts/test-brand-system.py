#!/usr/bin/env python3
"""Smoke tests for the independent Brand System Extension."""

import json
import subprocess
import sys
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
    for key in ["project_name", "source_query", "archetype", "personality", "logo_direction", "asset_brief"]:
        if key not in payload:
            raise AssertionError(f"Missing JSON key: {key}")
    if payload["project_name"] != "Assisted Dental Partners":
        raise AssertionError("Project name was not preserved in JSON output")

    conflict = run("test", "--brand-system", "--design-system")
    if conflict.returncode == 0:
        raise AssertionError("Mutually exclusive flags should fail")
    if "mutually exclusive" not in conflict.stderr:
        raise AssertionError(f"Expected mutual-exclusion error, got:\n{conflict.stderr}")

    print("Brand system smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
