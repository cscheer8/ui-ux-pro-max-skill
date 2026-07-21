#!/usr/bin/env python3
"""Validate Version 1.0 release metadata and neutral documentation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "VERSION",
    "CHANGELOG.md",
    "PREMIUM_STYLE_EXTENSION.md",
    "docs/installation-and-upgrade.md",
    "docs/release-v1.0.md",
    "examples/northstar-mobility/README.md",
    "examples/northstar-mobility/reference-manifest.json",
)
FORBIDDEN_EXAMPLE_NAMES = (
    "FieldOps Pro",
    "Assisted Dental Partners",
    "Bridgepoint OS",
)
NEUTRAL_DOCS = (
    "PREMIUM_STYLE_EXTENSION.md",
    "docs/installation-and-upgrade.md",
    "docs/release-v1.0.md",
    "examples/northstar-mobility/README.md",
)


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    assert not missing, f"Missing release files: {missing}"

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert version == "1.0.0", f"Expected VERSION 1.0.0, got {version!r}"

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## 1.0.0" in changelog
    assert "Legal boundary" in changelog

    for relative in NEUTRAL_DOCS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        found = [name for name in FORBIDDEN_EXAMPLE_NAMES if name in text]
        assert not found, f"{relative} contains external-project examples: {found}"

    manifest = json.loads(
        (ROOT / "examples/northstar-mobility/reference-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["schema_version"] == "1.0.0"
    assert manifest["fictional"] is True
    assert manifest["external_project_specific"] is False
    assert manifest["paid_image_generation"] == "explicit-opt-in"
    assert len(manifest["expected_capabilities"]) >= 8

    extension_guide = (ROOT / "PREMIUM_STYLE_EXTENSION.md").read_text(
        encoding="utf-8"
    )
    assert "does **not** copy" in extension_guide
    assert "--render-assets" in extension_guide
    assert "--complete-brand-package" in extension_guide

    print("Version 1.0 release metadata and neutral documentation validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
