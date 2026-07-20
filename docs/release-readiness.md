# Brand System Extension Release Readiness

Use this checklist before tagging a stable release. The governing feature scope is defined in [`premium-scope-roadmap.md`](premium-scope-roadmap.md). Optional extensions must not be treated as substitutes for unfinished core capabilities.

## Core premium-style capability gate

- [ ] Brand identity system generation is complete and documented.
- [ ] Logo workflows create finished logo concepts and required variants, not prompts alone.
- [ ] Corporate identity specifications cover coordinated core collateral.
- [ ] Banner and campaign families include dimensions, safe areas, hierarchy, and variants.
- [ ] Presentation systems generate valid structured outputs for every supported deck type.
- [ ] Custom iconography can produce consistent exported icon assets.
- [ ] At least one AI image-generation provider can create and save finished visual assets.
- [ ] Generated assets include prompt, provider, version, and provenance metadata.
- [ ] Enterprise token architecture supports documented inheritance, overrides, and version metadata.

## Functionality

- [ ] Complete package command succeeds in a clean directory.
- [ ] Existing packages are protected unless `--force` is supplied.
- [ ] Asset briefs and generation prompts are created.
- [ ] Finished generated assets are stored in predictable directories.
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

## Neutral validation scenarios

Run the complete workflow against at least two generic reference scenarios that exist only for skill validation:

- [ ] A fictional technical or industrial product.
- [ ] A fictional service or consumer-facing organization.

Do not use unrelated real projects as the governing examples for this repository.

For each reference scenario confirm:

- [ ] Brand archetype and personality are credible.
- [ ] Finished logo and imagery outputs are usable.
- [ ] Semantic colors meet the intended tone.
- [ ] Production exports integrate without hand correction.
- [ ] Audit findings have an acceptable false-positive rate.
- [ ] Presentation outlines match the selected deck purpose.
- [ ] Corporate identity and banner outputs follow the same brand system.

## Documentation and packaging

- [ ] Command guide is current.
- [ ] Generated directory structure is documented.
- [ ] Installation and upgrade instructions are current.
- [ ] Error recovery and `--force` behavior are documented.
- [ ] A neutral sample output package is included or linked.
- [ ] Release notes summarize new flags and outputs.
- [ ] Version number and tag are selected.
- [ ] Documentation does not imply official affiliation with a proprietary premium edition.

## Release gate

A stable release should not be tagged until:

1. All required CI checks are green.
2. Every core capability in the governing roadmap is complete rather than partial or missing.
3. Both neutral reference scenarios pass the validation checklist.
4. The legal and naming boundary remains clear.
