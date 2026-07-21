# Northstar Mobility — Neutral Reference Package

This fictional reference brand demonstrates the expected Version 1.0 output structure without using any external business or client project.

## Input

```text
regional mobility platform dependable clear modern accessible
```

## Expected package structure

```text
brand-system/northstar-mobility/
├── BRAND-SYSTEM.md
├── brand-system.json
├── asset-briefs/
├── presentation-system/
├── exports/
│   ├── css/
│   ├── tailwind/
│   ├── typescript/
│   ├── json/
│   ├── identity/
│   ├── corporate-identity/
│   └── enterprise-tokens/
└── audits/
```

## Generate the reference package

```bash
python src/ui-ux-pro-max/scripts/search.py \
  "regional mobility platform dependable clear modern accessible" \
  --complete-brand-package \
  --deck-type executive \
  -p "Northstar Mobility" \
  --output-dir "."
```

Then run the focused exporters:

```bash
python src/ui-ux-pro-max/scripts/export_identity.py \
  "regional mobility platform dependable clear modern accessible" \
  -p "Northstar Mobility" \
  --output-dir "." \
  --force

python src/ui-ux-pro-max/scripts/export_corporate_identity.py \
  "regional mobility platform dependable clear modern accessible" \
  -p "Northstar Mobility" \
  --output-dir "." \
  --force
```

The checked-in manifest beside this file is illustrative metadata, not a substitute for generated output.
