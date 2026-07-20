# Brand System Extension

The independent Brand System Extension adds persistent brand strategy, asset briefs, presentation systems, production token exports, and consistency auditing to UI UX Pro Max.

## Fastest complete workflow

```bash
python src/ui-ux-pro-max/scripts/search.py \
  "oilfield operations software rugged trustworthy modern" \
  --complete-brand-package \
  --deck-type executive \
  -p "FieldOps Pro" \
  --output-dir "."
```

`--complete-brand-package` is a convenience workflow equivalent to:

- `--brand-system`
- `--persist`
- `--generate-assets`
- `--presentation-system`
- `--export-tokens`

It creates a package under `brand-system/<project-slug>/`.

## Generated package

```text
brand-system/<project>/
├── MASTER.md
├── brand-system.json
├── assets/
│   ├── logo-brief.md
│   ├── icon-system.md
│   ├── image-direction.md
│   ├── social-kit.md
│   ├── presentation-system.md
│   └── generation-prompts.json
├── presentations/
│   ├── PRESENTATION-SYSTEM.md
│   ├── <deck-type>-deck-outline.md
│   ├── slide-layouts.json
│   ├── chart-style.json
│   └── generation-prompts.json
├── tokens/
│   └── semantic-brand-tokens.json
└── exports/
    ├── css/brand-tokens.css
    ├── tailwind/brand-theme.js
    ├── typescript/brand-tokens.ts
    ├── json/semantic-brand-tokens.json
    └── svg/emblem-template.svg
```

## Individual workflows

### Brand foundation

```bash
python src/ui-ux-pro-max/scripts/search.py \
  "trusted modern mobile dental care" \
  --brand-system --persist \
  -p "Assisted Dental Partners" \
  --output-dir "."
```

### Asset briefs and prompts

Add `--generate-assets`.

### Presentation system

Add `--presentation-system --deck-type pitch`.

Supported deck types are `pitch`, `sales`, `executive`, `training`, and `status`.

### Production tokens

Add:

```bash
--export-tokens --token-formats css,tailwind,typescript
```

### Brand audit

```bash
python src/ui-ux-pro-max/scripts/search.py \
  "oilfield operations software rugged trustworthy modern" \
  --brand-system --persist \
  --audit-brand --audit-path "./src" \
  -p "FieldOps Pro" \
  --output-dir "."
```

The audit writes Markdown and JSON reports under `brand-system/<project>/audits/`.

## Safe overwrite behavior

Persisted systems are not overwritten by default. Use `--force` only when deliberately regenerating an existing package.

## JSON automation

Add `--json` to receive structured output suitable for scripts and CI workflows.

## Recommended release workflow

1. Generate the complete package.
2. Review `MASTER.md`, the asset briefs, and the selected presentation outline.
3. Integrate the generated CSS, Tailwind, or TypeScript tokens.
4. Run the brand audit against the implementation directory.
5. Resolve errors first, then review warnings for intentional exceptions.
