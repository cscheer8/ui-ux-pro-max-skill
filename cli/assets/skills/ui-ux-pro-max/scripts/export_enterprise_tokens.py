#!/usr/bin/env python3
"""Generate a brand system and export a versioned multi-brand token architecture."""

import argparse
import json

from brand_system import generate_brand_system
from enterprise_tokens import export_enterprise_tokens


def _entity(value: str) -> dict:
    parts = value.split(":")
    item = {"name": parts[0].strip()}
    if len(parts) > 1 and parts[1].strip():
        item["primary"] = parts[1].strip()
    if len(parts) > 2 and parts[2].strip():
        item["accent"] = parts[2].strip()
    return item


def _product(value: str) -> dict:
    parts = value.split(":")
    item = {"name": parts[0].strip()}
    if len(parts) > 1 and parts[1].strip():
        item["brand"] = parts[1].strip()
    if len(parts) > 2 and parts[2].strip():
        item["primary"] = parts[2].strip()
    if len(parts) > 3 and parts[3].strip():
        item["accent"] = parts[3].strip()
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description="Export parent, child-brand, and product token inheritance")
    parser.add_argument("query", help="Parent brand and product-family description")
    parser.add_argument("--project-name", "-p", required=True, help="Parent brand name")
    parser.add_argument("--child-brand", action="append", default=[], type=_entity, metavar="NAME[:PRIMARY[:ACCENT]]")
    parser.add_argument("--product", action="append", default=[], type=_product, metavar="NAME[:BRAND[:PRIMARY[:ACCENT]]]")
    parser.add_argument("--token-version", default="1.0.0")
    parser.add_argument("--governance-status", choices=["draft", "review", "approved", "deprecated"], default="draft")
    parser.add_argument("--owner", default="Design Systems Team")
    parser.add_argument("--approver", default=None)
    parser.add_argument("--output-dir", "-o", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = generate_brand_system(args.query, args.project_name, output_format="markdown", persist=True, output_dir=args.output_dir, force=args.force)
    exported = export_enterprise_tokens(result["brand_system"], result["persistence"], child_brands=args.child_brand, products=args.product, version=args.token_version, governance_status=args.governance_status, owner=args.owner, approver=args.approver)
    payload = {"persistence": result["persistence"], "enterprise_tokens": exported}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif exported.get("status") == "created":
        print(f"Enterprise token architecture exported to {exported['manifest']}")
        print(f"Created {len(exported['created_files'])} files; inheritance validation passed.")
    else:
        print(exported.get("message", "Enterprise token export skipped."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
