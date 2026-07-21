#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a brand system and export corporate identity collateral and banners."""

import argparse
import json

from brand_system import generate_brand_system
from corporate_identity import export_corporate_identity


def main() -> int:
    parser = argparse.ArgumentParser(description="Export corporate identity collateral and banner families")
    parser.add_argument("query", help="Brand and product description")
    parser.add_argument("--project-name", "-p", required=True)
    parser.add_argument("--output-dir", "-o", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = generate_brand_system(
        args.query,
        args.project_name,
        output_format="markdown",
        persist=True,
        output_dir=args.output_dir,
        force=args.force,
    )
    exported = export_corporate_identity(result["brand_system"], result["persistence"])
    payload = {"persistence": result["persistence"], "corporate_identity": exported}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif exported.get("status") == "created":
        print(f"Corporate identity system exported to {exported['manifest']}")
        print(f"Created {len(exported['created_files'])} files; validation passed.")
    else:
        print(exported.get("message", "Corporate identity export skipped."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
