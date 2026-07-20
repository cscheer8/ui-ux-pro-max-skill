# Presentation System Milestone

## Scope

This milestone adds a persistent, provider-neutral presentation design system derived from an existing generated brand system.

## CLI

```bash
python search.py \
  "oilfield operations software for field teams" \
  --brand-system \
  --persist \
  --presentation-system \
  --deck-type executive \
  -p "FieldOps Pro" \
  --output-dir "<project-root>"
```

Supported deck types are `pitch`, `sales`, `executive`, `training`, and `status`.

## Persistent output

```text
brand-system/<project>/presentations/
├── PRESENTATION-SYSTEM.md
├── <deck-type>-deck-outline.md
├── slide-layouts.json
├── chart-style.json
└── generation-prompts.json
```

## Design requirements

- Inherit semantic brand colors and typography.
- Use a 16:9 canvas and a documented 12-column grid.
- Provide reusable cover, section, content, comparison, process, data, timeline, and closing layouts.
- Generate deck-type-specific narrative sequences.
- Include accessible chart and slide-writing rules.
- Remain provider-neutral so output can be used with PowerPoint, Canva, Figma, Google Slides, or an image-generation workflow.

## Validation

- Brand-system smoke tests generate and inspect all persistent files.
- Tests verify deck selection, outline length, grid structure, layout availability, chart rules, and invalid CLI combinations.
- Repository asset-sync checks confirm the source, CLI asset, and Claude skill mirrors match.
