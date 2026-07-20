#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brand System Generator for the independent Brand System Extension."""

import csv
import json
import re
from pathlib import Path
from core import BM25, DATA_DIR


BRAND_DOMAINS = {
    "archetype": {
        "file": "brand-archetypes.csv",
        "search_cols": ["Archetype", "Keywords", "Core Desire", "Brand Promise", "Best For"],
    },
    "personality": {
        "file": "brand-personalities.csv",
        "search_cols": ["Personality", "Keywords", "Voice Traits", "Best For"],
    },
    "logo": {
        "file": "logo-directions.csv",
        "search_cols": ["Direction", "Keywords", "Construction", "Best For", "Prompt Guidance"],
    },
}

TOKEN_PALETTES = {
    "Rugged Professional": {"primary": "#123B5D", "accent": "#F47A22", "surface": "#F5F7F8", "text": "#17212B"},
    "Trusted Modern": {"primary": "#17324D", "accent": "#2F6FED", "surface": "#F7F9FC", "text": "#18212F"},
    "Warm Expert": {"primary": "#245B67", "accent": "#D97745", "surface": "#FBF8F3", "text": "#273238"},
    "Bold Challenger": {"primary": "#171717", "accent": "#FF4D2E", "surface": "#FAFAFA", "text": "#171717"},
    "Refined Premium": {"primary": "#24201D", "accent": "#9A7448", "surface": "#F7F3EC", "text": "#201D1A"},
    "Playful Friendly": {"primary": "#5746D9", "accent": "#F05A8A", "surface": "#FAF9FF", "text": "#25213A"},
    "Technical Authority": {"primary": "#1E3347", "accent": "#00A3A3", "surface": "#F4F7FA", "text": "#15212C"},
    "Natural Grounded": {"primary": "#355844", "accent": "#B06F3C", "surface": "#F6F4ED", "text": "#253129"},
}


def _search_brand_domain(query: str, domain: str, max_results: int = 1) -> list:
    config = BRAND_DOMAINS[domain]
    filepath = DATA_DIR / config["file"]
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    documents = [" ".join(str(row.get(column, "")) for column in config["search_cols"]) for row in rows]
    index = BM25()
    index.fit(documents)
    ranked = index.score(query)
    results = []
    for row_index, score in ranked:
        if score <= 0:
            continue
        results.append(rows[row_index])
        if len(results) >= max_results:
            break
    return results


def _first(results: list, fallback: dict) -> dict:
    return results[0] if results else fallback


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "brand"


def _semantic_tokens(personality: dict) -> dict:
    name = personality.get("Personality", "Trusted Modern")
    palette = TOKEN_PALETTES.get(name, TOKEN_PALETTES["Trusted Modern"])
    return {
        "$schema": "https://design-tokens.github.io/community-group/format/",
        "metadata": {"personality": name, "version": "1.0.0"},
        "color": {
            "brand": {
                "primary": {"$type": "color", "$value": palette["primary"]},
                "accent": {"$type": "color", "$value": palette["accent"]},
            },
            "background": {
                "default": {"$type": "color", "$value": palette["surface"]},
                "inverse": {"$type": "color", "$value": "{color.brand.primary}"},
            },
            "text": {
                "default": {"$type": "color", "$value": palette["text"]},
                "inverse": {"$type": "color", "$value": "#FFFFFF"},
                "link": {"$type": "color", "$value": "{color.brand.accent}"},
            },
            "border": {
                "default": {"$type": "color", "$value": "#D8DEE5"},
                "focus": {"$type": "color", "$value": "{color.brand.accent}"},
            },
        },
        "typography": {
            "fontFamily": {
                "brand": {"$type": "fontFamily", "$value": ["Inter", "Arial", "sans-serif"]}
            },
            "fontWeight": {
                "regular": {"$type": "fontWeight", "$value": 400},
                "medium": {"$type": "fontWeight", "$value": 500},
                "bold": {"$type": "fontWeight", "$value": 700},
            },
        },
        "radius": {
            "sm": {"$type": "dimension", "$value": {"value": 4, "unit": "px"}},
            "md": {"$type": "dimension", "$value": {"value": 8, "unit": "px"}},
            "lg": {"$type": "dimension", "$value": {"value": 12, "unit": "px"}},
        },
    }


def _persist_brand_system(system: dict, markdown: str, output_dir: str = None, force: bool = False) -> dict:
    root = Path(output_dir).expanduser().resolve() if output_dir else Path.cwd()
    brand_dir = root / "brand-system" / _slugify(system["project_name"])
    master = brand_dir / "MASTER.md"
    if master.exists() and not force:
        return {
            "status": "skipped_exists",
            "brand_system_dir": str(brand_dir),
            "created_files": [],
            "message": f"{master} already exists; use --force to overwrite.",
        }

    assets_dir = brand_dir / "assets"
    tokens_dir = brand_dir / "tokens"
    assets_dir.mkdir(parents=True, exist_ok=True)
    tokens_dir.mkdir(parents=True, exist_ok=True)

    files = {
        master: markdown,
        brand_dir / "brand-system.json": json.dumps(system, indent=2, ensure_ascii=False) + "\n",
        tokens_dir / "semantic-brand-tokens.json": json.dumps(system["semantic_tokens"], indent=2, ensure_ascii=False) + "\n",
        assets_dir / "logo-brief.md": _format_logo_brief(system),
    }
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
    return {
        "status": "created",
        "brand_system_dir": str(brand_dir),
        "created_files": [str(path.relative_to(brand_dir)) for path in files],
    }


def generate_brand_system(query: str, project_name: str = None, output_format: str = "markdown", persist: bool = False, output_dir: str = None, force: bool = False) -> dict:
    """Generate a compact brand foundation and optionally persist it."""
    archetype = _first(_search_brand_domain(query, "archetype"), {
        "Archetype": "Sage", "Core Desire": "Create clarity and understanding",
        "Brand Promise": "Make better decisions with confidence", "Voice": "Clear, measured, practical",
        "Visual Direction": "Disciplined typography and structured layouts", "Avoid": "Unsupported claims and unnecessary jargon",
    })
    personality = _first(_search_brand_domain(query, "personality"), {
        "Personality": "Trusted Modern", "Voice Traits": "Calm; concise; confident",
        "Color Direction": "Navy, slate, restrained accent, generous white",
        "Typography Direction": "Contemporary humanist sans serif",
        "Imagery Direction": "Authentic people, environments, and proof points",
        "Interaction Character": "Predictable, accessible, quietly polished",
        "Avoid": "Generic gradients and vague innovation language",
    })
    logo = _first(_search_brand_domain(query, "logo"), {
        "Direction": "Geometric Emblem", "Construction": "Simple enclosed geometry with one dominant silhouette",
        "Color Strategy": "One primary color plus one accent; must work in one color",
        "Typography Pairing": "Sturdy sans serif wordmark",
        "Scalability Rules": "Recognizable at 24px with minimal interior detail",
        "Prompt Guidance": "Create a compact geometric emblem derived from the brand's core process.",
        "Avoid": "Literal clip art and tiny linework",
    })
    name = project_name or query.title()
    brand_system = {
        "project_name": name,
        "source_query": query,
        "archetype": archetype,
        "personality": personality,
        "logo_direction": logo,
        "semantic_tokens": _semantic_tokens(personality),
        "asset_brief": {
            "objective": f"Create a coherent identity for {name}",
            "brand_character": f"{personality.get('Personality', '')} with a {archetype.get('Archetype', '')} archetype",
            "logo_concept": logo.get("Prompt Guidance", ""),
            "required_versions": ["primary lockup", "standalone emblem", "one-color", "reversed", "favicon"],
            "constraints": [logo.get("Scalability Rules", ""), "Maintain accessible contrast in digital applications", "Do not depend on gradients or effects for recognition"],
        },
    }
    text = json.dumps(brand_system, indent=2, ensure_ascii=False) if output_format == "json" else _format_markdown(brand_system)
    persistence = _persist_brand_system(brand_system, text if output_format != "json" else _format_markdown(brand_system), output_dir, force) if persist else None
    return {"brand_system": brand_system, "text": text, "persistence": persistence}


def _format_logo_brief(system: dict) -> str:
    logo = system["logo_direction"]
    brief = system["asset_brief"]
    return f"""# {system['project_name']} — Logo Brief

## Objective
{brief['objective']}

## Direction
- **Concept:** {logo.get('Direction', '')}
- **Construction:** {logo.get('Construction', '')}
- **Color strategy:** {logo.get('Color Strategy', '')}
- **Typography pairing:** {logo.get('Typography Pairing', '')}
- **Scalability:** {logo.get('Scalability Rules', '')}

## Generation Prompt
{brief['logo_concept']}

## Required Deliverables
{chr(10).join(f'- {item}' for item in brief['required_versions'])}

## Avoid
{logo.get('Avoid', '')}
"""


def _format_markdown(system: dict) -> str:
    archetype = system["archetype"]
    personality = system["personality"]
    logo = system["logo_direction"]
    brief = system["asset_brief"]
    tokens = system["semantic_tokens"]["color"]
    return f"""# {system['project_name']} — Brand System

## Strategic Foundation

- **Primary archetype:** {archetype.get('Archetype', '')}
- **Core desire:** {archetype.get('Core Desire', '')}
- **Brand promise:** {archetype.get('Brand Promise', '')}
- **Brand personality:** {personality.get('Personality', '')}

## Voice and Character

- **Voice:** {archetype.get('Voice', personality.get('Voice Traits', ''))}
- **Voice traits:** {personality.get('Voice Traits', '')}
- **Interaction character:** {personality.get('Interaction Character', '')}

## Visual Identity

- **Visual direction:** {archetype.get('Visual Direction', '')}
- **Color direction:** {personality.get('Color Direction', '')}
- **Typography direction:** {personality.get('Typography Direction', '')}
- **Imagery direction:** {personality.get('Imagery Direction', '')}

## Semantic Color Tokens

- **Primary:** {tokens['brand']['primary']['$value']}
- **Accent:** {tokens['brand']['accent']['$value']}
- **Background:** {tokens['background']['default']['$value']}
- **Text:** {tokens['text']['default']['$value']}

## Logo Direction

- **Recommended direction:** {logo.get('Direction', '')}
- **Construction:** {logo.get('Construction', '')}
- **Color strategy:** {logo.get('Color Strategy', '')}
- **Typography pairing:** {logo.get('Typography Pairing', '')}
- **Scalability:** {logo.get('Scalability Rules', '')}

## Asset Creation Brief

- **Objective:** {brief['objective']}
- **Brand character:** {brief['brand_character']}
- **Logo concept:** {brief['logo_concept']}
- **Required versions:** {', '.join(brief['required_versions'])}

## Avoid

- {archetype.get('Avoid', '')}
- {personality.get('Avoid', '')}
- {logo.get('Avoid', '')}
"""
