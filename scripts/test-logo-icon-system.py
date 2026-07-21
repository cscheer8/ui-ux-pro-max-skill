#!/usr/bin/env python3
"""Smoke tests for production SVG logo and icon exports."""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "src" / "ui-ux-pro-max" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from brand_system import generate_brand_system
from logo_icon_system import ICON_NAMES, LOGO_VARIANTS, export_logo_icon_system


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        generated = generate_brand_system(
            "community banking dependable established clear",
            "Harbor Community Bank",
            persist=True,
            output_dir=temp,
        )
        result = export_logo_icon_system(generated["brand_system"], generated["persistence"])
        assert result["status"] == "created"
        assert result["validation"]["valid"] is True
        assert result["validation"]["stroke_widths"] == ["2"]

        brand_dir = Path(generated["persistence"]["brand_system_dir"])
        manifest = json.loads((brand_dir / "exports" / "identity" / "identity-manifest.json").read_text())
        assert len(manifest["logo_variants"]) == len(LOGO_VARIANTS)
        assert len(manifest["icons"]) == len(ICON_NAMES)
        assert manifest["small_size_target_px"] == 24
        assert manifest["icon_grid_px"] == 24
        assert manifest["icon_stroke_px"] == 2

        for filename in manifest["logo_variants"]:
            content = (brand_dir / "exports" / "identity" / "logos" / filename).read_text()
            assert "<svg" in content and "viewBox=" in content
        for filename in manifest["icons"]:
            content = (brand_dir / "exports" / "identity" / "icons" / filename).read_text()
            assert 'viewBox="0 0 24 24"' in content
            assert 'stroke-width="2"' in content

    print("Logo and icon system smoke tests passed")


if __name__ == "__main__":
    main()
