#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate persistent, brand-aware presentation systems and deck outlines."""

import json
from pathlib import Path


DECK_STRUCTURES = {
    "pitch": [
        ("Cover", "One-line value proposition and confident brand visual"),
        ("Problem", "Define the costly or frustrating status quo"),
        ("Opportunity", "Show why the timing and market conditions matter"),
        ("Solution", "Explain the product or service in one clear model"),
        ("How It Works", "Use a three-to-five-step process diagram"),
        ("Proof", "Show outcomes, traction, testimonials, or evidence"),
        ("Business Model", "Explain how value and revenue are created"),
        ("Go-to-Market", "Show acquisition channels and rollout sequence"),
        ("Roadmap", "Present milestones without false precision"),
        ("Team", "Connect experience directly to execution risk"),
        ("Ask", "State the decision, investment, or next step"),
    ],
    "sales": [
        ("Cover", "Customer-focused promise, not a company slogan"),
        ("Current State", "Reflect the buyer's operating reality"),
        ("Consequences", "Quantify delay, waste, risk, or missed upside"),
        ("Desired State", "Describe the practical future outcome"),
        ("Solution Overview", "Map capabilities to buyer priorities"),
        ("Workflow", "Show adoption and day-to-day use"),
        ("Evidence", "Use proof points and relevant customer stories"),
        ("Implementation", "Clarify timeline, responsibilities, and support"),
        ("Commercials", "Present packages or pricing with context"),
        ("Next Step", "Offer one low-friction action"),
    ],
    "executive": [
        ("Executive Summary", "Lead with decision, recommendation, and impact"),
        ("Context", "Provide only the background needed for the decision"),
        ("Key Findings", "Surface the three to five most material facts"),
        ("Options", "Compare realistic alternatives using consistent criteria"),
        ("Recommendation", "State the preferred path and rationale"),
        ("Financial Impact", "Show cost, return, risk, and assumptions"),
        ("Implementation", "Define owners, phases, and dependencies"),
        ("Decision Required", "Make the requested approval explicit"),
    ],
    "training": [
        ("Title and Outcomes", "State what participants will be able to do"),
        ("Why It Matters", "Connect the skill to real work"),
        ("Core Model", "Introduce the central framework"),
        ("Demonstration", "Show a correct worked example"),
        ("Guided Practice", "Provide a constrained exercise"),
        ("Common Mistakes", "Contrast correct and incorrect approaches"),
        ("Independent Practice", "Offer a realistic scenario"),
        ("Knowledge Check", "Test application rather than recall"),
        ("Job Aid", "Summarize the repeatable steps"),
        ("Next Actions", "Clarify follow-up and ownership"),
    ],
    "status": [
        ("Status Summary", "State overall health and the period covered"),
        ("Goals", "Restate the outcomes being managed"),
        ("Progress", "Show completed work and measurable movement"),
        ("Metrics", "Display only decision-relevant indicators"),
        ("Risks and Issues", "Name severity, owner, and mitigation"),
        ("Decisions Needed", "Separate blocked decisions from general updates"),
        ("Next Period", "List the next commitments and milestones"),
    ],
}


def _brand_colors(system: dict) -> dict:
    color = system["semantic_tokens"]["color"]
    return {
        "primary": color["brand"]["primary"]["$value"],
        "accent": color["brand"]["accent"]["$value"],
        "background": color["background"]["default"]["$value"],
        "text": color["text"]["default"]["$value"],
    }


def build_presentation_system(system: dict, deck_type: str = "pitch") -> dict:
    """Build a provider-neutral presentation specification."""
    if deck_type not in DECK_STRUCTURES:
        raise ValueError(f"Unsupported deck type: {deck_type}")

    colors = _brand_colors(system)
    personality = system["personality"]
    outline = [
        {"slide": index, "title": title, "purpose": purpose}
        for index, (title, purpose) in enumerate(DECK_STRUCTURES[deck_type], 1)
    ]
    return {
        "project_name": system["project_name"],
        "deck_type": deck_type,
        "format": {"aspect_ratio": "16:9", "canvas": "1920x1080", "safe_margin": "72px"},
        "grid": {"columns": 12, "gutter": "24px", "baseline": "8px", "content_width": "1536px"},
        "typography": {
            "family": system["semantic_tokens"]["typography"]["fontFamily"]["brand"]["$value"],
            "title": {"size": "54px", "weight": 700, "line_height": 1.05},
            "section": {"size": "40px", "weight": 700, "line_height": 1.1},
            "body": {"size": "26px", "weight": 400, "line_height": 1.3},
            "caption": {"size": "18px", "weight": 400, "line_height": 1.3},
        },
        "colors": colors,
        "visual_direction": personality.get("Imagery Direction", "Authentic, relevant imagery with clear proof points"),
        "slide_rules": [
            "One primary message per slide",
            "Use sentence-style headlines that state the takeaway",
            "Keep body copy below 45 words unless the slide is a reference appendix",
            "Prefer diagrams, evidence, and comparison over decorative imagery",
            "Maintain accessible contrast and never encode meaning by color alone",
        ],
        "layouts": {
            "cover": "Full-bleed or split composition with one headline, one supporting line, and restrained brand mark",
            "section": "Large section number or keyword with generous negative space",
            "content": "Headline plus two-column text-and-visual grid",
            "comparison": "Two or three aligned columns using identical criteria",
            "process": "Three to five horizontally sequenced steps with consistent icon treatment",
            "data": "One dominant chart with a takeaway headline and short source note",
            "timeline": "Milestone sequence with dates, owners, and dependencies",
            "closing": "Single decision or next action with contact or ownership information",
        },
        "chart_style": {
            "primary_series": colors["primary"],
            "highlight_series": colors["accent"],
            "neutral_series": ["#D8DEE5", "#AAB4BF", "#6B7785"],
            "gridlines": "Light and minimal",
            "labels": "Direct labels preferred over legends",
            "rules": ["Start quantitative axes at zero when comparison requires it", "Show units and source", "Avoid 3D effects"],
        },
        "outline": outline,
        "generation_prompt": (
            f"Create a {deck_type} presentation system for {system['project_name']}. "
            f"Use a {personality.get('Personality', 'Trusted Modern')} character, primary {colors['primary']}, "
            f"accent {colors['accent']}, disciplined 12-column layouts, accessible contrast, concise takeaway headlines, "
            "and editable diagrams. Avoid generic corporate gradients, crowded slides, and decorative charts."
        ),
    }


def _system_markdown(spec: dict) -> str:
    return f"""# {spec['project_name']} — Presentation System

## Foundation

- **Deck format:** {spec['format']['aspect_ratio']} ({spec['format']['canvas']})
- **Safe margin:** {spec['format']['safe_margin']}
- **Grid:** {spec['grid']['columns']} columns, {spec['grid']['gutter']} gutters, {spec['grid']['baseline']} baseline
- **Primary color:** {spec['colors']['primary']}
- **Accent color:** {spec['colors']['accent']}
- **Visual direction:** {spec['visual_direction']}

## Typography

- **Title:** {spec['typography']['title']['size']} / weight {spec['typography']['title']['weight']}
- **Section:** {spec['typography']['section']['size']} / weight {spec['typography']['section']['weight']}
- **Body:** {spec['typography']['body']['size']} / weight {spec['typography']['body']['weight']}
- **Caption:** {spec['typography']['caption']['size']}

## Slide Rules

{chr(10).join(f'- {rule}' for rule in spec['slide_rules'])}

## Standard Layouts

{chr(10).join(f"- **{name.title()}:** {description}" for name, description in spec['layouts'].items())}

## Chart Rules

{chr(10).join(f'- {rule}' for rule in spec['chart_style']['rules'])}
"""


def _outline_markdown(spec: dict) -> str:
    rows = "\n".join(
        f"## {item['slide']}. {item['title']}\n\n{item['purpose']}\n"
        for item in spec["outline"]
    )
    return f"# {spec['project_name']} — {spec['deck_type'].title()} Deck Outline\n\n{rows}"


def persist_presentation_system(system: dict, persistence: dict, deck_type: str = "pitch") -> dict:
    """Persist presentation rules into an existing brand-system package."""
    brand_dir_value = (persistence or {}).get("brand_system_dir")
    if not brand_dir_value:
        return {"status": "skipped", "created_files": [], "message": "Brand system persistence is required."}

    brand_dir = Path(brand_dir_value)
    target = brand_dir / "presentations"
    target.mkdir(parents=True, exist_ok=True)
    spec = build_presentation_system(system, deck_type)
    files = {
        target / "PRESENTATION-SYSTEM.md": _system_markdown(spec),
        target / f"{deck_type}-deck-outline.md": _outline_markdown(spec),
        target / "slide-layouts.json": json.dumps({"format": spec["format"], "grid": spec["grid"], "layouts": spec["layouts"]}, indent=2) + "\n",
        target / "chart-style.json": json.dumps(spec["chart_style"], indent=2) + "\n",
        target / "generation-prompts.json": json.dumps({"deck_type": deck_type, "prompt": spec["generation_prompt"], "outline": spec["outline"]}, indent=2) + "\n",
    }
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
    return {
        "status": "created",
        "presentation_dir": str(target),
        "deck_type": deck_type,
        "created_files": [str(path.relative_to(brand_dir)) for path in files],
        "presentation_system": spec,
    }
