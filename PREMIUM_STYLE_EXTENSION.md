# Premium-Style Extension — Version 1.0

This repository is a fork of the MIT-licensed UI UX Pro Max project. The original skill remains the foundation. This fork adds independently developed brand, identity, asset-generation, presentation, and enterprise-token capabilities.

This extension does **not** copy, contain, or claim exact parity with non-public proprietary premium files, hidden algorithms, hosted services, or priority-support benefits.

## Version 1.0 capabilities

- Brand strategy and persistent brand-system packages
- Logo-system and custom-icon SVG exports
- Corporate identity collateral and coordinated banner families
- Presentation-system guidance, layouts, chart rules, and outlines
- Provider-backed AI image generation with saved assets and provenance
- CSS, Tailwind, TypeScript, JSON, and enterprise token exports
- Parent/child/product token inheritance, overrides, migrations, and governance
- Brand consistency auditing

## Quick start

Generate a complete brand package without paid image rendering:

```bash
python src/ui-ux-pro-max/scripts/search.py \
  "regional mobility platform dependable clear modern" \
  --complete-brand-package \
  --deck-type executive \
  -p "Northstar Mobility" \
  --output-dir "."
```

Export editable logo and icon assets:

```bash
python src/ui-ux-pro-max/scripts/export_identity.py \
  "regional mobility platform dependable clear modern" \
  -p "Northstar Mobility" \
  --output-dir "."
```

Export corporate identity and banner families:

```bash
python src/ui-ux-pro-max/scripts/export_corporate_identity.py \
  "regional mobility platform dependable clear modern" \
  -p "Northstar Mobility" \
  --output-dir "."
```

Render finished image assets through OpenAI:

```bash
export OPENAI_API_KEY="your-key"
python src/ui-ux-pro-max/scripts/search.py \
  "regional mobility platform dependable clear modern" \
  --brand-system \
  --persist \
  --render-assets \
  --image-types logo,imagery,social_kit \
  -p "Northstar Mobility" \
  --output-dir "."
```

## Output location

Generated artifacts are stored beneath:

```text
brand-system/<project-slug>/
```

Existing files are protected unless the relevant command is explicitly run with `--force`.

## Documentation

- `docs/command-guide.md`
- `docs/installation-and-upgrade.md`
- `docs/release-v1.0.md`
- `docs/premium-scope-reconciliation.md`
- `docs/enterprise-token-architecture.md`

## Support boundary

This is a community-maintained software fork. Commercial service benefits associated with another product tier are not part of the software implementation.
