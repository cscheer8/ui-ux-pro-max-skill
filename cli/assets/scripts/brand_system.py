#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brand System Generator for the independent Brand System Extension."""

import csv
import json
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


def _search_brand_domain(query: str, domain: str, max_results: int = 1) -> list:
    config = BRAND_DOMAINS[domain]
    filepath = DATA_DIR / config["file"]
    if not filepath.exists():
        return []

    with open(filepath, "r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    documents = [
        " ".join(str(row.get(column, "")) for column in config["search_cols"])
        for row in rows
    ]
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


def generate_brand_system(query: str, project_name: str = None, output_format: str = "markdown") -> dict:
    """Generate a compact brand foundation from three independent datasets."""
    archetype = _first(_search_brand_domain(query, "archetype"), {
        "Archetype": "Sage",
        "Core Desire": "Create clarity and understanding",
        "Brand Promise": "Make better decisions with confidence",
        "Voice": "Clear, measured, practical",
        "Visual Direction": "Disciplined typography and structured layouts",
        "Avoid": "Unsupported claims and unnecessary jargon",
    })
    personality = _first(_search_brand_domain(query, "personality"), {
        "Personality": "Trusted Modern",
        "Voice Traits": "Calm; concise; confident",
        "Color Direction": "Navy, slate, restrained accent, generous white",
        "Typography Direction": "Contemporary humanist sans serif",
        "Imagery Direction": "Authentic people, environments, and proof points",
        "Interaction Character": "Predictable, accessible, quietly polished",
        "Avoid": "Generic gradients and vague innovation language",
    })
    logo = _first(_search_brand_domain(query, "logo"), {
        "Direction": "Geometric Emblem",
        "Construction": "Simple enclosed geometry with one dominant silhouette",
        "Color Strategy": "One primary color plus one accent; must work in one color",
        "Typography Pairing": "Sturdy sans serif wordmark",
        "Scalability Rules": "Recognizable at 24px with minimal interior detail",
        "Prompt Guidance": "Create a compact geometric emblem derived from the brand's core process.",
        "Avoid": "Literal clip art and tiny linework",
    })

    brand_system = {
        "project_name": project_name or query.title(),
        "source_query": query,
        "archetype": archetype,
        "personality": personality,
        "logo_direction": logo,
        "asset_brief": {
            "objective": f"Create a coherent identity for {project_name or query.title()}",
            "brand_character": f"{personality.get('Personality', '')} with a {archetype.get('Archetype', '')} archetype",
            "logo_concept": logo.get("Prompt Guidance", ""),
            "required_versions": ["primary lockup", "standalone emblem", "one-color", "reversed", "favicon"],
            "constraints": [
                logo.get("Scalability Rules", ""),
                "Maintain accessible contrast in digital applications",
                "Do not depend on gradients or effects for recognition",
            ],
        },
    }

    if output_format == "json":
        text = json.dumps(brand_system, indent=2, ensure_ascii=False)
    else:
        text = _format_markdown(brand_system)

    return {"brand_system": brand_system, "text": text}


def _format_markdown(system: dict) -> str:
    archetype = system["archetype"]
    personality = system["personality"]
    logo = system["logo_direction"]
    brief = system["asset_brief"]

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
