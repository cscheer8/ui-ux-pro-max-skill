#!/usr/bin/env python3
"""Export persisted semantic brand tokens to production formats."""

import json
from pathlib import Path

SUPPORTED_FORMATS = ("css", "tailwind", "typescript")


def _value(tokens: dict, *path: str):
    node = tokens
    for key in path:
        node = node[key]
    return node["$value"]


def _palette(tokens: dict) -> dict:
    return {
        "primary": _value(tokens, "color", "brand", "primary"),
        "accent": _value(tokens, "color", "brand", "accent"),
        "background": _value(tokens, "color", "background", "default"),
        "foreground": _value(tokens, "color", "text", "default"),
        "border": _value(tokens, "color", "border", "default"),
        "focus": _value(tokens, "color", "brand", "accent"),
        "inverse": _value(tokens, "color", "text", "inverse"),
    }


def _css(tokens: dict) -> str:
    p = _palette(tokens)
    return f""":root {{
  --brand-primary: {p['primary']};
  --brand-accent: {p['accent']};
  --background: {p['background']};
  --foreground: {p['foreground']};
  --border: {p['border']};
  --focus-ring: {p['focus']};
  --on-brand: {p['inverse']};
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}}

[data-theme=\"dark\"] {{
  --background: {p['foreground']};
  --foreground: {p['inverse']};
  --border: {p['primary']};
  --brand-primary: {p['accent']};
}}
"""


def _tailwind(tokens: dict) -> str:
    p = _palette(tokens)
    return f"""/** Generated from semantic-brand-tokens.json */
export default {{
  theme: {{
    extend: {{
      colors: {{
        brand: {{ primary: '{p['primary']}', accent: '{p['accent']}' }},
        background: '{p['background']}',
        foreground: '{p['foreground']}',
        border: '{p['border']}',
        ring: '{p['focus']}',
      }},
      borderRadius: {{ sm: '4px', md: '8px', lg: '12px' }},
      fontFamily: {{ brand: ['Inter', 'Arial', 'sans-serif'] }},
    }},
  }},
}};
"""


def _typescript(tokens: dict) -> str:
    p = _palette(tokens)
    payload = {
        "color": p,
        "radius": {"sm": "4px", "md": "8px", "lg": "12px"},
        "fontFamily": ["Inter", "Arial", "sans-serif"],
    }
    return "// Generated from semantic-brand-tokens.json\nexport const brandTokens = " + json.dumps(payload, indent=2) + " as const;\n\nexport type BrandTokens = typeof brandTokens;\n"


def export_tokens(brand_system: dict, persistence: dict, formats: list[str]) -> dict:
    if not persistence or persistence.get("status") != "created":
        return {"status": "skipped", "created_files": [], "message": "Brand system was not persisted."}
    unknown = [item for item in formats if item not in SUPPORTED_FORMATS]
    if unknown:
        raise ValueError(f"Unsupported token format(s): {', '.join(unknown)}")

    brand_dir = Path(persistence["brand_system_dir"])
    tokens = brand_system["semantic_tokens"]
    writers = {
        "css": (brand_dir / "exports" / "css" / "brand-tokens.css", _css),
        "tailwind": (brand_dir / "exports" / "tailwind" / "brand-theme.js", _tailwind),
        "typescript": (brand_dir / "exports" / "typescript" / "brand-tokens.ts", _typescript),
    }
    created = []
    for fmt in formats:
        path, render = writers[fmt]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(tokens), encoding="utf-8")
        created.append(str(path.relative_to(brand_dir)))

    json_path = brand_dir / "exports" / "json" / "semantic-brand-tokens.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(tokens, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    created.append(str(json_path.relative_to(brand_dir)))
    return {"status": "created", "formats": formats, "created_files": created}
