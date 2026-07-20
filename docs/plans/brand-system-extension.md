# Brand System Extension

## Objective

Extend the open-source UI/UX Pro Max skill with an independently developed brand-design workflow. The extension will generate a reusable brand foundation that can guide UI design, logos, marketing assets, presentations, iconography, imagery, and enterprise design tokens.

This work builds on the MIT-licensed repository while preserving its original copyright and license notices. It does not copy or claim to reproduce any non-public commercial edition.

## Initial User-Facing Command

```bash
python src/ui-ux-pro-max/scripts/search.py \
  "oilfield operations software rugged trustworthy modern" \
  --brand-system \
  -p "FieldOps Pro"
```

Planned persistence command:

```bash
python src/ui-ux-pro-max/scripts/search.py \
  "oilfield operations software rugged trustworthy modern" \
  --brand-system \
  --persist \
  -p "FieldOps Pro" \
  --output-dir "<project-root>"
```

## Version 1 Scope

The first release will generate:

1. Brand positioning and audience summary
2. Brand personality and archetype recommendations
3. Brand attributes and differentiators
4. Logo direction and construction guidance
5. Core and semantic color recommendations
6. Brand typography recommendations
7. Iconography direction
8. Photography and illustration direction
9. Voice and tone guidance
10. Presentation and marketing-asset direction
11. Brand anti-patterns and restrictions
12. A pre-delivery brand consistency checklist

## Architecture

### New source files

```text
src/ui-ux-pro-max/
├── data/
│   └── brand/
│       ├── archetypes.csv
│       ├── personalities.csv
│       ├── positioning.csv
│       ├── logo-directions.csv
│       ├── imagery.csv
│       ├── voice-tone.csv
│       └── reasoning.csv
├── scripts/
│   └── brand_system.py
└── schemas/
    └── brand-system.schema.json
```

### Existing files to extend

- `src/ui-ux-pro-max/scripts/core.py`
  - Register searchable brand domains.
- `src/ui-ux-pro-max/scripts/search.py`
  - Add `--brand-system` routing, output selection, JSON output, and persistence arguments.
- Platform templates and generated CLI assets
  - Document when agents should invoke the brand workflow.
- Validation and smoke-test scripts
  - Validate the new CSV files and exercise each new domain.

## Output Model

The internal result will use a stable dictionary/JSON shape:

```json
{
  "project": "FieldOps Pro",
  "query": "oilfield operations software rugged trustworthy modern",
  "positioning": {},
  "audience": {},
  "personality": {},
  "archetype": {},
  "logo": {},
  "colors": {},
  "typography": {},
  "iconography": {},
  "imagery": {},
  "voice_tone": {},
  "presentation": {},
  "asset_direction": {},
  "anti_patterns": [],
  "checklist": []
}
```

## Persistence Model

Brand output will be stored separately from page-level UI rules while remaining easy for agents to retrieve:

```text
brand-system/<project-slug>/
├── MASTER.md
├── brand-system.json
├── assets/
│   ├── logo-brief.md
│   ├── image-generation-brief.md
│   └── presentation-direction.md
└── tokens/
    └── semantic-brand-tokens.json
```

Existing files will not be overwritten unless `--force` is supplied.

## Implementation Phases

### Phase 1 — Foundation

- Add brand data schemas and starter datasets.
- Add brand domains to the BM25 search configuration.
- Implement `brand_system.py` recommendation synthesis.
- Add `--brand-system` to `search.py`.
- Support ASCII, Markdown, and JSON output.
- Add safe persistence behavior.

### Phase 2 — Design Tokens

- Generate core, semantic, and component-facing brand tokens.
- Add CSS custom-property output.
- Add Tailwind and TypeScript output adapters.
- Preserve aliases rather than duplicating raw values.

### Phase 3 — Asset Briefs

- Generate structured briefs for logos, icons, banners, presentation slides, photography, illustration, and AI-created imagery.
- Keep generation-provider integrations optional and separate from the deterministic recommendation engine.

### Phase 4 — Enterprise Features

- Multiple brand themes under one organization.
- Light, dark, and high-contrast token themes.
- Version metadata, deprecations, and migration guidance.
- Brand consistency audit across project files.

## Validation Requirements

Before merging Phase 1:

```bash
cd cli
npm ci
npm run sync:assets
npm run check:assets
npm run validate:csv
npm run smoke:domains
npm run smoke:stacks
npm run typecheck
npm run build
```

Additional tests must cover:

- `--brand-system` basic output
- `--brand-system --json`
- persistence without overwrite
- persistence with `--force`
- zero-result behavior without fabricated matches
- Windows UTF-8 output
- installation templates containing the updated skill instructions

## Naming and Attribution

Working feature name: **Brand System Extension**.

The repository and resulting distributions must retain the original MIT license and copyright notice. Documentation must describe this as an independent extension of the open-source project, not the official premium edition from the upstream author.
