#!/usr/bin/env python3
"""Smoke tests for brand consistency auditing."""

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
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        app_dir = project_root / "app"
        app_dir.mkdir()
        (app_dir / "styles.css").write_text(
            ":root { --brand-primary: #123B5D; }\n"
            ".approved { color: #123B5D; font-family: Inter, sans-serif; }\n"
            ".drift { color: #FF00FF; font-family: 'Comic Sans MS', cursive; }\n",
            encoding="utf-8",
        )

        result = run(
            "oilfield operations software rugged trustworthy modern",
            "--brand-system",
            "--persist",
            "--audit-brand",
            "--audit-path",
            str(app_dir),
            "-p",
            "FieldOps Pro",
            "--output-dir",
            str(project_root),
            "--json",
        )
        assert_success(result, "Brand audit command")
        payload = json.loads(result.stdout)
        audit = payload.get("brand_audit") or {}
        if audit.get("status") != "completed":
            raise AssertionError(f"Audit did not complete: {audit}")
        if audit.get("scanned_files") != 1:
            raise AssertionError(f"Expected one scanned file, got: {audit.get('scanned_files')}")
        codes = {issue["code"] for issue in audit.get("issues", [])}
        if "unapproved-color" not in codes:
            raise AssertionError(f"Rogue color was not detected: {audit}")
        if "unapproved-font" not in codes:
            raise AssertionError(f"Rogue font was not detected: {audit}")
        if audit.get("score", 100) >= 100:
            raise AssertionError("Audit score should be reduced by detected drift")

        brand_dir = project_root / "brand-system" / "fieldops-pro"
        json_report = brand_dir / "audits" / "brand-audit.json"
        md_report = brand_dir / "audits" / "brand-audit.md"
        if not json_report.exists() or not md_report.exists():
            raise AssertionError("Audit reports were not persisted")
        persisted = json.loads(json_report.read_text(encoding="utf-8"))
        if persisted["target_path"] != str(app_dir.resolve()):
            raise AssertionError("Audit report target path is incorrect")

    invalid = run("test", "--brand-system", "--persist", "--audit-brand")
    if invalid.returncode == 0 or "requires --brand-system --persist --audit-path" not in invalid.stderr:
        raise AssertionError("--audit-brand without --audit-path should fail")

    orphan_path = run("test", "--brand-system", "--persist", "--audit-path", ".")
    if orphan_path.returncode == 0 or "requires --audit-brand" not in orphan_path.stderr:
        raise AssertionError("--audit-path without --audit-brand should fail")

    print("Brand audit smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
