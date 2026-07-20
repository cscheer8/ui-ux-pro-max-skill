#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persist provider-neutral brand asset briefs and exports."""

from pathlib import Path

from asset_generation import build_asset_package, serialize_prompts


def persist_asset_package(system: dict, persistence: dict) -> dict:
    """Write generated assets into an already-created persistent brand package."""
    if not persistence or persistence.get("status") not in {"created", "overwritten"}:
        return {
            "status": "skipped",
            "created_files": [],
            "message": "Brand system was not persisted; asset generation requires a writable persistent package.",
        }

    brand_dir = Path(persistence["brand_system_dir"])
    assets_dir = brand_dir / "assets"
    exports_dir = brand_dir / "exports" / "svg"
    assets_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)

    package = build_asset_package(system)
    files = {assets_dir / "generation-prompts.json": serialize_prompts(package)}
    for filename, content in package["briefs"].items():
        files[assets_dir / filename] = content
    for filename, content in package["svg_exports"].items():
        files[exports_dir / filename] = content

    for path, content in files.items():
        path.write_text(content, encoding="utf-8")

    return {
        "status": "created",
        "asset_dir": str(assets_dir),
        "created_files": [str(path.relative_to(brand_dir)) for path in files],
    }
