#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provider-neutral asset briefs, prompts, and deterministic SVG exports."""

import json
from html import escape


def _value(system: dict, path: tuple, fallback: str = "") -> str:
    current = system
    for key in path:
        current = current.get(key, {}) if isinstance(current, dict) else {}
    return current if isinstance(current, str) else fallback


def build_asset_package(system: dict) -> dict:
    """Build structured briefs and prompts from a generated brand system."""
    name = system["project_name"]
    personality = system["personality"]
    archetype = system["archetype"]
    logo = system["logo_direction"]
    colors = system["semantic_tokens"]["color"]

    primary = colors["brand"]["primary"]["$value"]
    accent = colors["brand"]["accent"]["$value"]
    surface = colors["background"]["default"]["$value"]
    text = colors["text"]["default"]["$value"]
    character = f"{personality.get('Personality', '')} with a {archetype.get('Archetype', '')} archetype"

    prompts = {
        "metadata": {"project": name, "version": "1.0.0", "provider": "provider-neutral"},
        "logo": {
            "prompt": (
                f"Design a professional logo system for {name}. Brand character: {character}. "
                f"Direction: {logo.get('Direction', '')}. Construction: {logo.get('Construction', '')}. "
                f"Use {primary} as the primary color and {accent} as the accent. "
                f"The mark must work in one color, remain recognizable at 24px, and avoid {logo.get('Avoid', '')}."
            ),
            "negative_prompt": "mockup scene, photorealistic object, tiny linework, illegible text, gradients required for recognition",
            "deliverables": ["primary lockup", "standalone emblem", "one-color", "reversed", "favicon"],
        },
        "icon_system": {
            "prompt": (
                f"Create a coherent custom icon family for {name}. Use a 24px grid, 2px optical stroke, rounded joins, "
                f"minimal interior detail, and the {character} brand character. Use {primary} and {accent} sparingly."
            ),
            "negative_prompt": "mixed stroke widths, emoji styling, clip art, perspective inconsistency, excessive detail",
            "deliverables": ["navigation icons", "status icons", "feature icons", "one-color SVG set"],
        },
        "imagery": {
            "prompt": (
                f"Create authentic brand imagery for {name}. Direction: {personality.get('Imagery Direction', '')}. "
                f"Visual tone: {archetype.get('Visual Direction', '')}. Use natural environments, credible details, "
                f"restrained composition, and subtle accents derived from {primary} and {accent}."
            ),
            "negative_prompt": "generic stock-photo poses, fake dashboards, exaggerated cinematic lighting, text overlays, visual clutter",
            "deliverables": ["hero image", "feature image set", "team or customer imagery", "background textures"],
        },
        "social_kit": {
            "prompt": (
                f"Design a modular social media system for {name} using {primary}, {accent}, {surface}, and {text}. "
                f"Maintain clear hierarchy, generous safe zones, strong contrast, and a {personality.get('Personality', '')} tone."
            ),
            "negative_prompt": "template marketplace look, decorative clutter, low contrast, more than two display typefaces",
            "deliverables": ["square post", "portrait post", "story", "profile banner", "announcement card"],
        },
        "presentation": {
            "prompt": (
                f"Create a presentation visual system for {name}. Use structured layouts, clear evidence hierarchy, "
                f"accessible charts, restrained use of {accent}, and the brand voice: {personality.get('Voice Traits', '')}."
            ),
            "negative_prompt": "dense text walls, decorative charts, random gradients, inconsistent alignment, tiny labels",
            "deliverables": ["cover", "section divider", "content slide", "data slide", "comparison slide", "closing slide"],
        },
    }

    briefs = {
        "icon-system.md": _icon_brief(system),
        "image-direction.md": _image_brief(system),
        "social-kit.md": _social_brief(system),
        "presentation-system.md": _presentation_brief(system),
    }
    return {
        "generation_prompts": prompts,
        "briefs": briefs,
        "svg_exports": {"emblem-template.svg": _emblem_svg(system)},
    }


def _icon_brief(system: dict) -> str:
    name = system["project_name"]
    return f"""# {name} — Icon System

## Construction
- 24px base grid
- 2px optical stroke
- Rounded joins and caps
- Minimal interior detail
- One dominant metaphor per icon

## Usage
- Navigation icons should remain neutral until active.
- Status icons may use the brand accent only when meaning requires emphasis.
- All icons must remain understandable without color.

## Avoid
- Mixed perspectives
- Decorative clip art
- Emoji-like rendering
- Inconsistent stroke weights
"""


def _image_brief(system: dict) -> str:
    p = system["personality"]
    a = system["archetype"]
    return f"""# {system['project_name']} — Image Direction

## Direction
- **Imagery:** {p.get('Imagery Direction', '')}
- **Visual tone:** {a.get('Visual Direction', '')}
- **Brand character:** {p.get('Personality', '')}

## Composition
- Prefer credible environments and real operational detail.
- Leave intentional negative space for optional interface or campaign copy.
- Use brand colors as subtle environmental accents, not artificial overlays.

## Avoid
- Generic stock-photo gestures
- Overstaged scenes
- Fake interface screenshots
- Text baked into generated imagery
"""


def _social_brief(system: dict) -> str:
    colors = system["semantic_tokens"]["color"]
    return f"""# {system['project_name']} — Social Kit

## Core Formats
- Square post: 1080 × 1080
- Portrait post: 1080 × 1350
- Story: 1080 × 1920
- Profile banner: platform-specific safe area

## Visual Rules
- Primary: {colors['brand']['primary']['$value']}
- Accent: {colors['brand']['accent']['$value']}
- Background: {colors['background']['default']['$value']}
- Use one clear message per asset.
- Keep logos and text inside generous safe zones.
- Maintain accessible contrast.
"""


def _presentation_brief(system: dict) -> str:
    return f"""# {system['project_name']} — Presentation System

## Slide Families
- Cover
- Section divider
- Narrative content
- Data and chart
- Comparison
- Process diagram
- Closing and next steps

## Rules
- One primary idea per slide.
- Use short headlines that state the conclusion.
- Keep charts direct and label data near the mark.
- Use the accent color only for emphasis and active comparisons.
- Preserve consistent margins, title position, and footer treatment.
"""


def _emblem_svg(system: dict) -> str:
    colors = system["semantic_tokens"]["color"]
    primary = colors["brand"]["primary"]["$value"]
    accent = colors["brand"]["accent"]["$value"]
    surface = colors["background"]["default"]["$value"]
    initials = "".join(part[0] for part in system["project_name"].split()[:3] if part).upper() or "B"
    title = escape(system["project_name"])
    initials = escape(initials)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-labelledby="title desc">
  <title id="title">{title} emblem construction template</title>
  <desc id="desc">Editable geometric emblem template generated from the brand color tokens.</desc>
  <rect width="512" height="512" rx="96" fill="{surface}"/>
  <circle cx="256" cy="256" r="176" fill="{primary}"/>
  <path d="M256 112 L378 326 H134 Z" fill="{accent}" opacity="0.92"/>
  <circle cx="256" cy="256" r="76" fill="{surface}"/>
  <text x="256" y="278" text-anchor="middle" font-family="Arial, sans-serif" font-size="64" font-weight="700" fill="{primary}">{initials}</text>
</svg>
'''


def serialize_prompts(asset_package: dict) -> str:
    return json.dumps(asset_package["generation_prompts"], indent=2, ensure_ascii=False) + "\n"
