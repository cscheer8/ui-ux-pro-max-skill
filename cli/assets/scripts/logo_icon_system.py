#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate deterministic, editable SVG logo variants and icon families."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from xml.etree import ElementTree

LOGO_VARIANTS = ("horizontal", "stacked", "emblem", "monochrome", "reversed", "favicon")
ICON_NAMES = ("home", "search", "user", "settings", "check", "alert", "calendar", "chart")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "brand"


def _colors(system: dict) -> tuple[str, str, str, str]:
    tokens = system["semantic_tokens"]["color"]
    return (
        tokens["brand"]["primary"]["$value"],
        tokens["brand"]["accent"]["$value"],
        tokens["background"]["default"]["$value"],
        tokens["text"]["default"]["$value"],
    )


def _initials(name: str) -> str:
    return "".join(part[0] for part in name.split()[:3] if part).upper() or "B"


def _mark(system: dict, *, fill_primary: str, fill_accent: str, surface: str) -> str:
    initials = escape(_initials(system["project_name"]))
    return f'''<rect x="8" y="8" width="112" height="112" rx="26" fill="{surface}"/>
<circle cx="64" cy="64" r="42" fill="{fill_primary}"/>
<path d="M64 28 L96 84 H32 Z" fill="{fill_accent}"/>
<circle cx="64" cy="64" r="18" fill="{surface}"/>
<text x="64" y="70" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="{fill_primary}">{initials}</text>'''


def _svg(viewbox: str, body: str, title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" role="img" aria-label="{escape(title)}">
{body}
</svg>
'''


def _logo_variants(system: dict) -> dict[str, str]:
    name = escape(system["project_name"])
    primary, accent, surface, text = _colors(system)
    mark = _mark(system, fill_primary=primary, fill_accent=accent, surface=surface)
    mono_mark = _mark(system, fill_primary="#000000", fill_accent="#000000", surface="#FFFFFF")
    reversed_mark = _mark(system, fill_primary="#FFFFFF", fill_accent=accent, surface=primary)
    return {
        "logo-horizontal.svg": _svg("0 0 520 128", f'{mark}\n<text x="150" y="76" font-family="Arial, sans-serif" font-size="42" font-weight="700" fill="{text}">{name}</text>', f"{name} horizontal logo"),
        "logo-stacked.svg": _svg("0 0 320 250", f'<g transform="translate(96 10)">{mark}</g>\n<text x="160" y="210" text-anchor="middle" font-family="Arial, sans-serif" font-size="34" font-weight="700" fill="{text}">{name}</text>', f"{name} stacked logo"),
        "logo-emblem.svg": _svg("0 0 128 128", mark, f"{name} emblem"),
        "logo-monochrome.svg": _svg("0 0 520 128", f'{mono_mark}\n<text x="150" y="76" font-family="Arial, sans-serif" font-size="42" font-weight="700" fill="#000000">{name}</text>', f"{name} monochrome logo"),
        "logo-reversed.svg": _svg("0 0 520 128", f'<rect width="520" height="128" fill="{primary}"/>\n{reversed_mark}\n<text x="150" y="76" font-family="Arial, sans-serif" font-size="42" font-weight="700" fill="#FFFFFF">{name}</text>', f"{name} reversed logo"),
        "favicon.svg": _svg("0 0 128 128", mark, f"{name} favicon"),
    }


def _icon_paths() -> dict[str, str]:
    return {
        "home": '<path d="M4 11 12 4l8 7v9h-6v-6h-4v6H4z"/>',
        "search": '<circle cx="11" cy="11" r="6"/><path d="m16 16 5 5"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1-5 4-7 8-7s7 2 8 7"/>',
        "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9 7 7M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"/>',
        "check": '<path d="m4 13 5 5L20 6"/>',
        "alert": '<path d="M12 3 2.5 21h19z"/><path d="M12 9v5M12 18h.01"/>',
        "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>',
        "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    }


def _icon_svg(name: str, primary: str) -> str:
    body = _icon_paths()[name]
    return _svg("0 0 24 24", f'<g fill="none" stroke="{primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</g>', f"{name} icon")


def validate_svg_system(files: dict[str, str]) -> dict:
    errors: list[str] = []
    stroke_widths: set[str] = set()
    for filename, content in files.items():
        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as exc:
            errors.append(f"{filename}: invalid SVG: {exc}")
            continue
        if not root.attrib.get("viewBox"):
            errors.append(f"{filename}: missing viewBox")
        for element in root.iter():
            width = element.attrib.get("stroke-width")
            if width:
                stroke_widths.add(width)
    if len(stroke_widths) > 1:
        errors.append(f"icon stroke widths are inconsistent: {sorted(stroke_widths)}")
    return {"valid": not errors, "errors": errors, "stroke_widths": sorted(stroke_widths), "file_count": len(files)}


def export_logo_icon_system(system: dict, persistence: dict) -> dict:
    if not persistence or persistence.get("status") not in {"created", "overwritten"}:
        return {"status": "skipped", "created_files": [], "message": "Logo and icon export requires a writable persisted brand package."}
    brand_dir = Path(persistence["brand_system_dir"])
    logo_dir = brand_dir / "exports" / "identity" / "logos"
    icon_dir = brand_dir / "exports" / "identity" / "icons"
    logo_dir.mkdir(parents=True, exist_ok=True)
    icon_dir.mkdir(parents=True, exist_ok=True)
    logos = _logo_variants(system)
    primary, _, _, _ = _colors(system)
    icons = {f"icon-{name}.svg": _icon_svg(name, primary) for name in ICON_NAMES}
    all_files = {**logos, **icons}
    validation = validate_svg_system(all_files)
    if not validation["valid"]:
        raise ValueError("Generated identity system failed validation: " + "; ".join(validation["errors"]))
    created: list[str] = []
    for filename, content in logos.items():
        path = logo_dir / filename
        path.write_text(content, encoding="utf-8")
        created.append(str(path.relative_to(brand_dir)))
    for filename, content in icons.items():
        path = icon_dir / filename
        path.write_text(content, encoding="utf-8")
        created.append(str(path.relative_to(brand_dir)))
    manifest = {"schema_version": "1.0.0", "project": system["project_name"], "logo_variants": list(logos), "icons": list(icons), "small_size_target_px": 24, "icon_grid_px": 24, "icon_stroke_px": 2, "validation": validation}
    manifest_path = brand_dir / "exports" / "identity" / "identity-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    created.append(str(manifest_path.relative_to(brand_dir)))
    return {"status": "created", "created_files": created, "manifest": str(manifest_path), "validation": validation}
