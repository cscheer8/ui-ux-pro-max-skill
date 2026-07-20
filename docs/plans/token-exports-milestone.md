# Production Token Exports Milestone

This milestone converts the persisted semantic brand token source into deployable platform files.

## Outputs

- CSS custom properties with light and dark theme aliases
- Tailwind theme extension
- Typed TypeScript constants
- Canonical JSON copy of the semantic token source

## Invariants

- Platform exports must use the values in `semantic-brand-tokens.json`.
- Unsupported format names fail at CLI validation.
- `--export-tokens` requires `--brand-system --persist`.
- Generated mirrors must remain synchronized with `src/ui-ux-pro-max`.
