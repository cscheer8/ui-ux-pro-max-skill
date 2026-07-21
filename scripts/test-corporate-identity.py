#!/usr/bin/env python3
"""Smoke-test corporate identity collateral and banner-family exports."""

import json
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "src" / "ui-ux-pro-max" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from brand_system import generate_brand_system  # noqa: E402
from corporate_identity import BANNER_FORMATS, COLLATERAL_FORMATS, export_corporate_identity  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        generated = generate_brand_system(
            "regional financial cooperative established clear accessible",
            "Harbor Cooperative",
            persist=True,
            output_dir=tmp,
        )
        result = export_corporate_identity(generated["brand_system"], generated["persistence"])
        assert result["status"] == "created"
        assert result["validation"]["valid"] is True
        assert len(result["created_files"]) == 12

        brand_dir = Path(generated["persistence"]["brand_system_dir"])
        root = brand_dir / "exports" / "corporate-identity"
        manifest = json.loads((root / "corporate-identity-manifest.json").read_text(encoding="utf-8"))
        assert set(manifest["collateral"]) == set(COLLATERAL_FORMATS)
        assert set(manifest["banners"]) == set(BANNER_FORMATS)
        assert manifest["validation"]["svg_count"] == 10

        for relative in result["created_files"]:
            path = brand_dir / relative
            assert path.exists(), relative
            if path.suffix == ".svg":
                root_element = ElementTree.fromstring(path.read_text(encoding="utf-8"))
                assert root_element.attrib.get("viewBox")

        signature = (root / "collateral" / "email-signature.html").read_text(encoding="utf-8")
        assert "role=\"presentation\"" in signature
        assert "mailto:email@example.com" in signature

        skipped = export_corporate_identity(generated["brand_system"], {"status": "skipped_exists"})
        assert skipped["status"] == "skipped"

    print("Corporate identity and banner smoke test passed.")


if __name__ == "__main__":
    main()
