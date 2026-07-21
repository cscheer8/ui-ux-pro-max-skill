# Logo and Icon Output Systems

This workflow exports a coordinated, editable SVG identity system from the generated brand foundation.

## Command

```bash
python src/ui-ux-pro-max/scripts/export_identity.py \
  "community banking dependable established clear" \
  -p "Harbor Community Bank" \
  --output-dir "."
```

Use `--force` to replace an existing persisted brand package.

## Output

```text
brand-system/<project>/exports/identity/
├── identity-manifest.json
├── logos/
│   ├── logo-horizontal.svg
│   ├── logo-stacked.svg
│   ├── logo-emblem.svg
│   ├── logo-monochrome.svg
│   ├── logo-reversed.svg
│   └── favicon.svg
└── icons/
    ├── icon-home.svg
    ├── icon-search.svg
    ├── icon-user.svg
    ├── icon-settings.svg
    ├── icon-check.svg
    ├── icon-alert.svg
    ├── icon-calendar.svg
    └── icon-chart.svg
```

## Validation

The exporter verifies that every file is valid XML/SVG, every asset has a `viewBox`, all icons use the same 24-pixel grid, and all icon strokes use the same two-pixel optical weight. The manifest records the small-size target and validation result.

These SVG outputs are deterministic and editable. They complement provider-rendered visual concepts rather than depending on raster generation for production identity files.
