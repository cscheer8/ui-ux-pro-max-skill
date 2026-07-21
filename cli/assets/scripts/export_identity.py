#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a persisted brand system and export production SVG identity assets."""

import argparse
import json

from brand_system import generate_brand_system
from logo_icon_system import export_logo_icon_system


def main() -> int:
    parser = argparse.ArgumentParser(description="Export logo variants and a custom SVG icon family")
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
    identity = export_logo_icon_system(result["brand_system"], result["persistence"])
    payload = {
        "persistence": result["persistence"],
        "identity_exports": identity,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif identity.get("status") == "created":
        print(f"Identity system exported to {identity['manifest']}")
        print(f"Created {len(identity['created_files'])} files; validation passed.")
    else:
        print(identity.get("message", "Identity export skipped."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
