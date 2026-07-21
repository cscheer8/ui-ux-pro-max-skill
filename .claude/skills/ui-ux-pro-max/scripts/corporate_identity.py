#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export editable corporate identity collateral and coordinated banner families."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from xml.etree import ElementTree

COLLATERAL_FORMATS = {
    "business-card-front.svg": {"viewBox": "0 0 1050 600", "width_in": 3.5, "height_in": 2.0},
    "business-card-back.svg": {"viewBox": "0 0 1050 600", "width_in": 3.5, "height_in": 2.0},
    "letterhead.svg": {"viewBox": "0 0 2550 3300", "width_in": 8.5, "height_in": 11.0},
    "document-cover.svg": {"viewBox": "0 0 2550 3300", "width_in": 8.5, "height_in": 11.0},
}

BANNER_FORMATS = {
    "web-hero.svg": {"viewBox": "0 0 1920 720", "width_px": 1920, "height_px": 720, "safe_area": [120, 90, 1800, 630]},
    "campaign-banner.svg": {"viewBox": "0 0 1600 900", "width_px": 1600, "height_px": 900, "safe_area": [96, 72, 1504, 828]},
    "social-landscape.svg": {"viewBox": "0 0 1200 628", "width_px": 1200, "height_px": 628, "safe_area": [72, 56, 1128, 572]},
    "social-square.svg": {"viewBox": "0 0 1080 1080", "width_px": 1080, "height_px": 1080, "safe_area": [72, 72, 1008, 1008]},
    "social-story.svg": {"viewBox": "0 0 1080 1920", "width_px": 1080, "height_px": 1920, "safe_area": [72, 180, 1008, 1740]},
    "presentation-banner.svg": {"viewBox": "0 0 1920 360", "width_px": 1920, "height_px": 360, "safe_area": [120, 54, 1800, 306]},
}


def _colors(system: dict) -> tuple[str, str, str, str]:
    tokens = system["semantic_tokens"]["color"]
    return (
        tokens["brand"]["primary"]["$value"],
        tokens["brand"]["accent"]["$value"],
        tokens["background"]["default"]["$value"],
        tokens["text"]["default"]["$value"],
    )


def _svg(viewbox: str, body: str, title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" role="img" aria-label="{escape(title)}">
{body}
</svg>
'''


def _mark(system: dict, x: int, y: int, scale: float = 1.0) -> str:
    primary, accent, surface, _ = _colors(system)
    size = int(120 * scale)
    radius = int(26 * scale)
    cx = x + size // 2
    cy = y + size // 2
    tri = f"{cx},{y + int(18*scale)} {x + int(102*scale)},{y + int(92*scale)} {x + int(18*scale)},{y + int(92*scale)}"
    return (
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{radius}" fill="{surface}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{int(44*scale)}" fill="{primary}"/>'
        f'<polygon points="{tri}" fill="{accent}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{int(18*scale)}" fill="{surface}"/>'
    )


def _business_cards(system: dict) -> dict[str, str]:
    name = escape(system["project_name"])
    primary, accent, surface, text = _colors(system)
    front = _svg(
        COLLATERAL_FORMATS["business-card-front.svg"]["viewBox"],
        f'''<rect width="1050" height="600" fill="{surface}"/>
<rect width="32" height="600" fill="{accent}"/>
{_mark(system, 72, 70, 0.9)}
<text x="210" y="130" font-family="Arial, sans-serif" font-size="54" font-weight="700" fill="{primary}">{name}</text>
<text x="72" y="360" font-family="Arial, sans-serif" font-size="38" font-weight="700" fill="{text}">Your Name</text>
<text x="72" y="408" font-family="Arial, sans-serif" font-size="26" fill="{text}">Title or Department</text>
<text x="72" y="500" font-family="Arial, sans-serif" font-size="24" fill="{text}">email@example.com  ·  +1 555 010 2020</text>
<rect x="48" y="48" width="954" height="504" fill="none" stroke="{accent}" stroke-width="2" stroke-dasharray="12 12" opacity="0.35"/>''',
        f"{name} business card front",
    )
    back = _svg(
        COLLATERAL_FORMATS["business-card-back.svg"]["viewBox"],
        f'''<rect width="1050" height="600" fill="{primary}"/>
{_mark(system, 405, 155, 2.0)}
<text x="525" y="500" text-anchor="middle" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#FFFFFF">{name}</text>''',
        f"{name} business card back",
    )
    return {"business-card-front.svg": front, "business-card-back.svg": back}


def _letterhead(system: dict) -> str:
    name = escape(system["project_name"])
    primary, accent, surface, text = _colors(system)
    return _svg(
        COLLATERAL_FORMATS["letterhead.svg"]["viewBox"],
        f'''<rect width="2550" height="3300" fill="#FFFFFF"/>
<rect width="2550" height="34" fill="{accent}"/>
{_mark(system, 170, 120, 1.2)}
<text x="350" y="220" font-family="Arial, sans-serif" font-size="82" font-weight="700" fill="{primary}">{name}</text>
<text x="350" y="286" font-family="Arial, sans-serif" font-size="34" fill="{text}">Address · City, State ZIP · example.com</text>
<line x1="170" y1="390" x2="2380" y2="390" stroke="{primary}" stroke-width="5"/>
<rect x="170" y="500" width="2210" height="2460" fill="none" stroke="{surface}" stroke-width="4" stroke-dasharray="18 18"/>
<text x="170" y="3170" font-family="Arial, sans-serif" font-size="28" fill="{text}">{name} · Confidential when marked</text>''',
        f"{name} letterhead",
    )


def _document_cover(system: dict) -> str:
    name = escape(system["project_name"])
    primary, accent, surface, text = _colors(system)
    return _svg(
        COLLATERAL_FORMATS["document-cover.svg"]["viewBox"],
        f'''<rect width="2550" height="3300" fill="{surface}"/>
<rect x="0" y="0" width="760" height="3300" fill="{primary}"/>
<rect x="760" y="0" width="36" height="3300" fill="{accent}"/>
{_mark(system, 170, 180, 2.2)}
<text x="940" y="1420" font-family="Arial, sans-serif" font-size="138" font-weight="700" fill="{text}">Document Title</text>
<text x="940" y="1540" font-family="Arial, sans-serif" font-size="52" fill="{text}">Subtitle, report type, or campaign name</text>
<text x="940" y="2870" font-family="Arial, sans-serif" font-size="44" font-weight="700" fill="{primary}">{name}</text>
<text x="940" y="2940" font-family="Arial, sans-serif" font-size="34" fill="{text}">Month Year · Version 1.0</text>''',
        f"{name} document cover",
    )


def _email_signature(system: dict) -> str:
    name = escape(system["project_name"])
    primary, accent, _, text = _colors(system)
    return f'''<!doctype html>
<html><body>
<table role="presentation" cellpadding="0" cellspacing="0" style="font-family:Arial,sans-serif;color:{text};line-height:1.35">
<tr><td style="padding-right:18px;border-right:4px solid {accent}">
<div style="width:62px;height:62px;border-radius:14px;background:{primary};color:#fff;text-align:center;line-height:62px;font-size:22px;font-weight:700">{escape(''.join(p[0] for p in system['project_name'].split()[:3]).upper())}</div>
</td><td style="padding-left:18px">
<div style="font-size:18px;font-weight:700;color:{primary}">Your Name</div>
<div style="font-size:14px">Title · {name}</div>
<div style="font-size:13px;margin-top:7px">+1 555 010 2020 · <a href="mailto:email@example.com" style="color:{primary}">email@example.com</a></div>
<div style="font-size:12px;margin-top:5px;color:#666">example.com · Address, City, State ZIP</div>
</td></tr></table>
</body></html>
'''


def _banner(system: dict, filename: str, spec: dict) -> str:
    name = escape(system["project_name"])
    primary, accent, surface, text = _colors(system)
    _, _, width, height = map(int, spec["viewBox"].split())
    left, top, right, bottom = spec["safe_area"]
    headline_size = max(44, int(width * 0.055))
    sub_size = max(24, int(width * 0.024))
    return _svg(
        spec["viewBox"],
        f'''<rect width="{width}" height="{height}" fill="{surface}"/>
<path d="M{int(width*.64)} 0 H{width} V{height} H{int(width*.48)} Z" fill="{primary}"/>
<circle cx="{int(width*.83)}" cy="{int(height*.42)}" r="{int(min(width,height)*.23)}" fill="{accent}" opacity="0.92"/>
<text x="{left}" y="{int(top + (bottom-top)*.36)}" font-family="Arial, sans-serif" font-size="{headline_size}" font-weight="700" fill="{text}">Campaign headline</text>
<text x="{left}" y="{int(top + (bottom-top)*.52)}" font-family="Arial, sans-serif" font-size="{sub_size}" fill="{text}">One clear supporting message with room to breathe.</text>
<rect x="{left}" y="{int(top + (bottom-top)*.66)}" width="{int(width*.17)}" height="{int(height*.11)}" rx="{int(height*.025)}" fill="{accent}"/>
<text x="{left + int(width*.085)}" y="{int(top + (bottom-top)*.735)}" text-anchor="middle" font-family="Arial, sans-serif" font-size="{max(20,int(width*.017))}" font-weight="700" fill="#FFFFFF">Call to action</text>
<text x="{left}" y="{bottom}" font-family="Arial, sans-serif" font-size="{max(18,int(width*.015))}" font-weight="700" fill="{primary}">{name}</text>
<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" fill="none" stroke="{accent}" stroke-width="3" stroke-dasharray="18 14" opacity="0.4"/>''',
        f"{name} {filename.replace('-', ' ').replace('.svg', '')}",
    )


def validate_corporate_identity(files: dict[str, str], manifest: dict) -> dict:
    errors: list[str] = []
    svg_files = {name: content for name, content in files.items() if name.endswith(".svg")}
    for filename, content in svg_files.items():
        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as exc:
            errors.append(f"{filename}: invalid SVG: {exc}")
            continue
        if not root.attrib.get("viewBox"):
            errors.append(f"{filename}: missing viewBox")
    for filename, spec in manifest["banners"].items():
        left, top, right, bottom = spec["safe_area"]
        if not (0 <= left < right <= spec["width_px"] and 0 <= top < bottom <= spec["height_px"]):
            errors.append(f"{filename}: invalid safe area")
    required = set(COLLATERAL_FORMATS) | set(BANNER_FORMATS) | {"email-signature.html"}
    missing = sorted(required - set(files))
    if missing:
        errors.append("missing required outputs: " + ", ".join(missing))
    return {"valid": not errors, "errors": errors, "file_count": len(files), "svg_count": len(svg_files)}


def export_corporate_identity(system: dict, persistence: dict) -> dict:
    if not persistence or persistence.get("status") not in {"created", "overwritten"}:
        return {"status": "skipped", "created_files": [], "message": "Corporate identity export requires a writable persisted brand package."}

    brand_dir = Path(persistence["brand_system_dir"])
    root = brand_dir / "exports" / "corporate-identity"
    collateral_dir = root / "collateral"
    banner_dir = root / "banners"
    collateral_dir.mkdir(parents=True, exist_ok=True)
    banner_dir.mkdir(parents=True, exist_ok=True)

    collateral = {
        **_business_cards(system),
        "letterhead.svg": _letterhead(system),
        "document-cover.svg": _document_cover(system),
        "email-signature.html": _email_signature(system),
    }
    banners = {filename: _banner(system, filename, spec) for filename, spec in BANNER_FORMATS.items()}
    all_files = {**collateral, **banners}
    manifest = {
        "schema_version": "1.0.0",
        "project": system["project_name"],
        "collateral": COLLATERAL_FORMATS,
        "email_signature": {"format": "HTML", "table_based": True, "inline_styles": True},
        "banners": BANNER_FORMATS,
        "copy_hierarchy": ["brand", "headline", "supporting message", "call to action"],
        "rules": ["keep critical text inside safe areas", "use one primary message per banner", "preserve accessible contrast", "do not stretch the logo"],
    }
    validation = validate_corporate_identity(all_files, manifest)
    if not validation["valid"]:
        raise ValueError("Generated corporate identity failed validation: " + "; ".join(validation["errors"]))
    manifest["validation"] = validation

    created: list[str] = []
    for filename, content in collateral.items():
        path = collateral_dir / filename
        path.write_text(content, encoding="utf-8")
        created.append(str(path.relative_to(brand_dir)))
    for filename, content in banners.items():
        path = banner_dir / filename
        path.write_text(content, encoding="utf-8")
        created.append(str(path.relative_to(brand_dir)))
    manifest_path = root / "corporate-identity-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    created.append(str(manifest_path.relative_to(brand_dir)))
    return {"status": "created", "created_files": created, "manifest": str(manifest_path), "validation": validation}
