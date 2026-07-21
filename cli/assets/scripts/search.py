#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/UX Pro Max search and system generation CLI."""

import argparse
import io
import json as json_module
import sys

from core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, UNTRUNCATED_COLS, search, search_stack
from design_system import generate_design_system
from brand_system import generate_brand_system
from asset_persist import persist_asset_package
from presentation_system import persist_presentation_system
from token_exports import SUPPORTED_FORMATS, export_tokens
from brand_audit import audit_brand_system
from image_execution import (
    SUPPORTED_IMAGE_TYPES,
    SUPPORTED_OUTPUT_FORMATS,
    SUPPORTED_QUALITIES,
    SUPPORTED_SIZES,
    execute_image_generation,
    get_provider,
)

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

TRUNCATE_AT = 300


def format_output(result, full=False):
    if "error" in result:
        return f"Error: {result['error']}"
    output = []
    if result.get("stack"):
        output.extend(["## UI Pro Max Stack Guidelines", f"**Stack:** {result['stack']} | **Query:** {result['query']}"])
    else:
        output.append("## UI Pro Max Search Results")
        domain_note = result["domain"]
        if result.get("auto_detected"):
            domain_note += " (auto-detected"
            if result.get("runner_up_domain"):
                domain_note += f", runner-up: {result['runner_up_domain']}"
            domain_note += ")"
        output.append(f"**Domain:** {domain_note} | **Query:** {result['query']}")
    output.append(f"**Source:** {result['file']} | **Found:** {result['count']} results\n")
    if result["count"] == 0:
        output.append("No matches. Retry with broader or different keywords before falling back to general defaults.")
        if result.get("suggestions"):
            output.append(f"**Closest known terms:** {', '.join(result['suggestions'])}")
        return "\n".join(output)
    for index, row in enumerate(result["results"], 1):
        output.append(f"### Result {index}")
        for key, value in row.items():
            value_str = str(value)
            if not full and key not in UNTRUNCATED_COLS and len(value_str) > TRUNCATE_AT:
                value_str = value_str[:TRUNCATE_AT] + "..."
            output.append(f"- **{key}:** {value_str}")
        output.append("")
    return "\n".join(output)


def print_persistence(result: dict, label: str) -> None:
    persistence = result.get("persistence") or {}
    print("\n" + "=" * 60)
    if persistence.get("status") == "skipped_exists":
        print(f"⚠️  {persistence.get('message', 'Existing system was not overwritten.')}")
    else:
        target = persistence.get("brand_system_dir") or persistence.get("design_system_dir") or f"{label}/<project>"
        print(f"✅ {label.replace('-', ' ').title()} persisted to {target}/")
        for filename in persistence.get("created_files", []):
            print(f"   📄 {filename}")
    sections = [
        ("asset_generation", "🎨 Asset briefs and prompts generated"),
        ("image_execution", "🖼️ Finished image assets generated"),
        ("presentation_generation", "📊 Presentation system generated"),
        ("token_exports", "🧩 Production token exports generated"),
    ]
    for key, heading in sections:
        generated = result.get(key) or {}
        if generated.get("status") == "created":
            print(f"\n{heading}:")
            for filename in generated.get("created_files", []):
                print(f"   📄 {filename}")
    audit = result.get("brand_audit") or {}
    if audit.get("status") == "completed":
        print(f"\n🔎 Brand audit completed: {audit.get('score', 0)}/100")
        print(f"   Errors: {audit.get('summary', {}).get('error', 0)} | Warnings: {audit.get('summary', {}).get('warning', 0)}")
        for filename in audit.get("created_files", []):
            print(f"   📄 {filename}")
    print("=" * 60)


def parse_formats(raw: str) -> list[str]:
    formats = [item.strip().lower() for item in raw.split(",") if item.strip()]
    unknown = [item for item in formats if item not in SUPPORTED_FORMATS]
    if unknown:
        raise argparse.ArgumentTypeError(f"unsupported token format(s): {', '.join(unknown)}")
    return formats


def parse_image_types(raw: str) -> list[str]:
    image_types = [item.strip().lower().replace("-", "_") for item in raw.split(",") if item.strip()]
    unknown = [item for item in image_types if item not in SUPPORTED_IMAGE_TYPES]
    if unknown:
        raise argparse.ArgumentTypeError(f"unsupported image type(s): {', '.join(unknown)}")
    return image_types


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI Pro Max Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Search domain")
    parser.add_argument("--stack", "-s", choices=AVAILABLE_STACKS, help="Stack-specific search")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--design-system", "-ds", action="store_true")
    parser.add_argument("--brand-system", "-bs", action="store_true")
    parser.add_argument("--complete-brand-package", action="store_true", help="Generate the persisted brand system, asset briefs, presentation system, and all token exports")
    parser.add_argument("--generate-assets", action="store_true", help="Generate provider-neutral briefs and prompts; does not call an image provider")
    parser.add_argument("--render-assets", action="store_true", help="Call an image provider and save finished generated image files")
    parser.add_argument("--image-provider", choices=["openai"], default="openai")
    parser.add_argument("--image-types", type=parse_image_types, default=list(SUPPORTED_IMAGE_TYPES), help="Comma-separated: logo,icon_system,imagery,social_kit")
    parser.add_argument("--image-model", default="gpt-image-1")
    parser.add_argument("--image-size", choices=SUPPORTED_SIZES, default="1024x1024")
    parser.add_argument("--image-quality", choices=SUPPORTED_QUALITIES, default="auto")
    parser.add_argument("--image-format", choices=SUPPORTED_OUTPUT_FORMATS, default="png")
    parser.add_argument("--image-attempts", type=int, default=3)
    parser.add_argument("--regenerate-from", default=None, help="Prior asset_id recorded as the source of a regeneration")
    parser.add_argument("--presentation-system", action="store_true")
    parser.add_argument("--deck-type", choices=["pitch", "sales", "executive", "training", "status"], default="pitch")
    parser.add_argument("--export-tokens", action="store_true", help="Export persisted semantic tokens for production use")
    parser.add_argument("--token-formats", type=parse_formats, default=list(SUPPORTED_FORMATS), help="Comma-separated: css,tailwind,typescript")
    parser.add_argument("--audit-brand", action="store_true", help="Audit a project directory against the persisted brand system")
    parser.add_argument("--audit-path", default=None, help="Project file or directory to scan during a brand audit")
    parser.add_argument("--project-name", "-p", default=None)
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii")
    parser.add_argument("--persist", action="store_true")
    parser.add_argument("--page", default=None)
    parser.add_argument("--output-dir", "-o", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--variance", type=int, choices=range(1, 11), metavar="1-10")
    parser.add_argument("--motion", type=int, choices=range(1, 11), metavar="1-10")
    parser.add_argument("--density", type=int, choices=range(1, 11), metavar="1-10")
    args = parser.parse_args()

    if args.complete_brand_package:
        args.brand_system = True
        args.persist = True
        args.generate_assets = True
        args.presentation_system = True
        args.export_tokens = True
    if args.render_assets:
        args.generate_assets = True

    if args.design_system and args.brand_system:
        parser.error("--design-system and --brand-system are mutually exclusive")
    if args.persist and not (args.design_system or args.brand_system):
        parser.error("--persist requires --design-system or --brand-system")
    if args.generate_assets and not (args.brand_system and args.persist):
        parser.error("--generate-assets requires --brand-system --persist")
    if args.render_assets and not (args.brand_system and args.persist):
        parser.error("--render-assets requires --brand-system --persist")
    if args.image_attempts < 1:
        parser.error("--image-attempts must be at least 1")
    if args.regenerate_from and not args.render_assets:
        parser.error("--regenerate-from requires --render-assets")
    if args.presentation_system and not (args.brand_system and args.persist):
        parser.error("--presentation-system requires --brand-system --persist")
    if args.deck_type != "pitch" and not args.presentation_system:
        parser.error("--deck-type requires --presentation-system")
    if args.export_tokens and not (args.brand_system and args.persist):
        parser.error("--export-tokens requires --brand-system --persist")
    if args.audit_brand and not (args.brand_system and args.persist and args.audit_path):
        parser.error("--audit-brand requires --brand-system --persist --audit-path")
    if args.audit_path and not args.audit_brand:
        parser.error("--audit-path requires --audit-brand")

    if args.brand_system:
        result = generate_brand_system(args.query, args.project_name, output_format="json" if args.json else "markdown", persist=args.persist, output_dir=args.output_dir, force=args.force)
        result["asset_generation"] = persist_asset_package(result["brand_system"], result["persistence"]) if args.generate_assets else None
        result["image_execution"] = None
        if args.render_assets:
            try:
                result["image_execution"] = execute_image_generation(
                    result["brand_system"],
                    result["persistence"],
                    provider=get_provider(args.image_provider),
                    image_types=args.image_types,
                    model=args.image_model,
                    size=args.image_size,
                    quality=args.image_quality,
                    output_format=args.image_format,
                    attempts=args.image_attempts,
                    regenerate_from=args.regenerate_from,
                )
            except (RuntimeError, ValueError) as exc:
                parser.error(str(exc))
        result["presentation_generation"] = persist_presentation_system(result["brand_system"], result["persistence"], args.deck_type) if args.presentation_system else None
        result["token_exports"] = export_tokens(result["brand_system"], result["persistence"], args.token_formats) if args.export_tokens else None
        result["brand_audit"] = audit_brand_system(result["brand_system"], result["persistence"], args.audit_path) if args.audit_brand else None
        if args.json:
            payload = result["brand_system"] if not args.persist else {
                "brand_system": result["brand_system"],
                "persistence": result["persistence"],
                "asset_generation": result["asset_generation"],
                "image_execution": result["image_execution"],
                "presentation_generation": result["presentation_generation"],
                "token_exports": result["token_exports"],
                "brand_audit": result["brand_audit"],
            }
            print(json_module.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(result["text"])
        if args.persist and not args.json:
            print_persistence(result, "brand-system")
    elif args.design_system:
        result = generate_design_system(args.query, args.project_name, args.format, persist=args.persist, page=args.page, output_dir=args.output_dir, variance=args.variance, motion=args.motion, density=args.density, force=args.force)
        print(json_module.dumps({"design_system": result["design_system"], "persistence": result["persistence"]}, indent=2, ensure_ascii=False) if args.json else result["text"])
        if args.persist and not args.json:
            print_persistence(result, "design-system")
    elif args.stack:
        result = search_stack(args.query, args.stack, args.max_results)
        print(json_module.dumps(result, indent=2, ensure_ascii=False) if args.json else format_output(result, full=args.full))
    else:
        result = search(args.query, args.domain, args.max_results)
        print(json_module.dumps(result, indent=2, ensure_ascii=False) if args.json else format_output(result, full=args.full))
