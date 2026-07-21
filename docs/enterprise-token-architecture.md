# Enterprise Token Architecture

This workflow extends a persisted semantic brand system into a versioned parent/child/product token architecture.

## Example

```bash
python src/ui-ux-pro-max/scripts/export_enterprise_tokens.py \
  "global logistics platform dependable clear scalable" \
  -p "Atlas Group" \
  --child-brand "Atlas Europe:#1144AA:#EE9900" \
  --product "Atlas Dispatch:Atlas Europe::#00AA88" \
  --token-version "2.1.0" \
  --governance-status review \
  --owner "Enterprise Design Systems" \
  --approver "Design Council" \
  --output-dir "."
```

## Output

```text
brand-system/<project>/exports/enterprise-tokens/
├── foundation.json
├── governance.json
├── migrations.json
├── enterprise-token-manifest.json
├── brands/
│   └── <child-brand>.json
└── products/
    └── <product>.json
```

Each child brand inherits the parent foundation. Each product inherits either the parent brand or a named child brand. Overrides are applied recursively, while untouched token branches remain inherited. Every resolved node records its inheritance chain and explicit overrides.

Governance metadata includes lifecycle status, owner, approver, timestamps, and approval requirements. Migration records identify source and target versions, migration type, breaking status, and notes.
