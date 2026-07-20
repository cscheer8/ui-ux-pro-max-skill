#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Search - BM25 search engine for UI/UX style guides
Usage: python search.py "<query>" [--domain <domain>] [--stack <stack>] [--max-results 3]
       python search.py "<query>" --design-system [-p "Project Name"]
       python search.py "<query>" --brand-system [-p "Project Name"]
       python search.py "<query>" --brand-system --persist --generate-assets -p "Project Name" --output-dir "<project-root>"
       python search.py "<query>" --design-system --persist [-p "Project Name"] --output-dir "<project-root>" [--page "dashboard"]
       python search.py "<query>" --design-system --variance 8 --motion 9 --density 7

Domains: style, color, chart, landing, product, ux, typography, google-fonts, icons, gsap, react, web
Stacks: react, nextjs, vue, svelte, astro, swiftui, react-native, flutter, nuxtjs, nuxt-ui,
        html-tailwind, shadcn, jetpack-compose, threejs, angular, laravel
"""

import argparse
import json as json_module
import sys
import io
from core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, UNTRUNCATED_COLS, search, search_stack
from design_system import generate_design_system
from brand_system import generate_brand_system
from asset_persist import persist_asset_package

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

TRUNCATE_AT = 300


def format_output(result, full=False):
    """Format results for Claude consumption (token-optimized)."""
    if "error" in result:
        return f"Error: {result['error']}"
    output = []
    if result.get("stack"):
        output.append("## UI Pro Max Stack Guidelines")
        output.append(f"**Stack:** {result['stack']} | **Query:** {result['query']}")
    else:
        output.append("## UI Pro Max Search Results")
        domain_note = result['domain']
        if result.get("auto_detected"):
            domain_note += " (auto-detected"
            if result.get("runner_up_domain"):
                domain_note += f", runner-up: {result['runner_up_domain']}"
            domain_note += ")"
        output.append(f"**Domain:** {domain_note} | **Query:** {result['query']}")
    output.append(f"**Source:** {result['file']} | **Found:** {result['count']} results\n")
    if result['count'] == 0:
        output.append("No matches. This is not a match with an empty value -- the query did not hit the database. Retry with broader/different keywords before falling back to general defaults, and say explicitly that no database match was found if you do fall back.")
        suggestions = result.get("suggestions") or []
        if suggestions:
            output.append(f"**Closest known terms:** {', '.join(suggestions)}")
        return "\n".join(output)
    for i, row in enumerate(result['results'], 1):
        output.append(f"### Result {i}")
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
    asset_generation = result.get("asset_generation") or {}
    if asset_generation.get("status") == "created":
        print("\n🎨 Asset package generated:")
        for filename in asset_generation.get("created_files", []):
            print(f"   📄 {filename}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI Pro Max Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Search domain")
    parser.add_argument("--stack", "-s", choices=AVAILABLE_STACKS, help=f"Stack-specific search. Available: {', '.join(AVAILABLE_STACKS)}")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS, help="Max results (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--full", action="store_true", help="Do not truncate long field values in text output")
    parser.add_argument("--design-system", "-ds", action="store_true", help="Generate complete design system recommendation")
    parser.add_argument("--brand-system", "-bs", action="store_true", help="Generate an independent brand identity system recommendation")
    parser.add_argument("--generate-assets", action="store_true", help="Generate provider-neutral brand briefs, prompts, and SVG exports (requires --brand-system --persist)")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name for design or brand system output")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii", help="Output format for design system (ignored if --json)")
    parser.add_argument("--persist", action="store_true", help="Persist the generated design or brand system")
    parser.add_argument("--page", type=str, default=None, help="Create page-specific override file for a design system")
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Project root under which the system folder is created")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing persisted system")
    parser.add_argument("--variance", type=int, choices=range(1, 11), metavar="1-10", help="DESIGN_VARIANCE dial (only with --design-system)")
    parser.add_argument("--motion", type=int, choices=range(1, 11), metavar="1-10", help="MOTION_INTENSITY dial (only with --design-system)")
    parser.add_argument("--density", type=int, choices=range(1, 11), metavar="1-10", help="VISUAL_DENSITY dial (only with --design-system)")
    args = parser.parse_args()

    if args.design_system and args.brand_system:
        parser.error("--design-system and --brand-system are mutually exclusive")
    if args.persist and not (args.design_system or args.brand_system):
        parser.error("--persist requires --design-system or --brand-system")
    if args.generate_assets and not (args.brand_system and args.persist):
        parser.error("--generate-assets requires --brand-system --persist")

    if args.brand_system:
        result = generate_brand_system(
            args.query,
            args.project_name,
            output_format="json" if args.json else "markdown",
            persist=args.persist,
            output_dir=args.output_dir,
            force=args.force,
        )
        result["asset_generation"] = persist_asset_package(result["brand_system"], result["persistence"]) if args.generate_assets else None
        if args.json:
            if args.persist:
                payload = {
                    "brand_system": result["brand_system"],
                    "persistence": result["persistence"],
                    "asset_generation": result["asset_generation"],
                }
            else:
                payload = result["brand_system"]
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
