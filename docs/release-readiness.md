# Brand System Extension Release Readiness

Use this checklist before tagging a stable release.

## Functionality

- [ ] Complete package command succeeds on a clean directory.
- [ ] Existing packages are protected unless `--force` is supplied.
- [ ] Asset briefs and generation prompts are created.
- [ ] Every presentation deck type generates a valid outline.
- [ ] CSS, Tailwind, TypeScript, and JSON tokens match the semantic source.
- [ ] Brand auditing detects deliberate color and typography drift.
- [ ] Markdown and JSON audit reports are readable and actionable.

## Compatibility

- [ ] Python 3.10–3.12 smoke tests pass.
- [ ] Windows paths containing spaces are covered by manual validation.
- [ ] Linux CI passes.
- [ ] Mirrored CLI and Claude skill assets match the source tree.
- [ ] Existing design-system and search workflows remain unchanged.

## Real-project validation

Run the complete workflow against at least two distinct projects:

- [ ] A technical or industrial product.
- [ ] A healthcare, service, or consumer-facing organization.

For each project confirm:

- [ ] Brand archetype and personality are credible.
- [ ] Logo and imagery direction are usable.
- [ ] Semantic colors meet the intended tone.
- [ ] Production exports integrate without hand correction.
- [ ] Audit findings have an acceptable false-positive rate.
- [ ] Presentation outlines match the selected deck purpose.

## Documentation

- [ ] Command guide is current.
- [ ] Generated directory structure is documented.
- [ ] Error recovery and `--force` behavior are documented.
- [ ] Release notes summarize new flags and outputs.
- [ ] Version number and tag are selected.

## Release gate

A stable release should not be tagged until all required CI checks are green and the two-project validation is complete.
