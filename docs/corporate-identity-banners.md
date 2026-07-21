# Corporate Identity and Banner Exports

Generate editable corporate identity collateral and a coordinated banner family from one brand-system query.

```bash
python src/ui-ux-pro-max/scripts/export_corporate_identity.py \
  "regional financial cooperative established clear accessible" \
  -p "Harbor Cooperative" \
  --output-dir "."
```

Use `--force` to replace an existing persisted package. Use `--json` for machine-readable command output.

## Output

```text
brand-system/<project>/exports/corporate-identity/
├── corporate-identity-manifest.json
├── collateral/
│   ├── business-card-front.svg
│   ├── business-card-back.svg
│   ├── letterhead.svg
│   ├── document-cover.svg
│   └── email-signature.html
└── banners/
    ├── web-hero.svg
    ├── campaign-banner.svg
    ├── social-landscape.svg
    ├── social-square.svg
    ├── social-story.svg
    └── presentation-banner.svg
```

The manifest records physical or pixel dimensions, banner safe areas, copy hierarchy, usage rules, and validation results. SVG assets are editable and use the persisted semantic brand colors. The HTML email signature uses table-based markup and inline styles for broad email-client compatibility.
