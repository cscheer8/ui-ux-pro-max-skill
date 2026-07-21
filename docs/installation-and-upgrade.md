# Installation and Upgrade

## Requirements

- Python 3.10 or newer
- Git
- Node.js only for the repository's browser smoke tests and CLI packaging workflows
- `OPENAI_API_KEY` only when explicitly rendering image assets through the OpenAI provider

## Install from this repository

```bash
git clone https://github.com/cscheer8/ui-ux-pro-max-skill.git
cd ui-ux-pro-max-skill
python src/ui-ux-pro-max/scripts/search.py --help
```

The Python workflows use the standard library and repository data files. No paid provider is contacted by default.

## Install the skill into a project

Use the repository's existing installation method for the target agent or copy the synchronized skill directory from one of these locations:

```text
src/ui-ux-pro-max/
cli/assets/skills/ui-ux-pro-max/
.claude/skills/ui-ux-pro-max/
```

`src/ui-ux-pro-max/` is the source of truth. The bundled copies are validated in CI and should not be edited independently.

## Upgrade an existing clone

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
```

Review `CHANGELOG.md` before upgrading generated brand packages. Version 1.0 preserves the original search/design-system behavior and adds new explicit commands.

## Generated-package safety

The extension writes generated artifacts beneath:

```text
brand-system/<project-slug>/
```

Commands avoid overwriting an existing package unless `--force` is explicitly supplied. Back up hand-edited generated files before forcing regeneration.

## Image provider setup

Image rendering is opt-in:

```bash
export OPENAI_API_KEY="your-key"
```

Without that environment variable, non-rendering workflows remain available. `--complete-brand-package` does not silently trigger paid image generation.

## Verify an installation

```bash
python scripts/validate-csv.py
python scripts/test-brand-system.py
python scripts/test-release-workflow.py
python scripts/test-logo-icon-system.py
python scripts/test-corporate-identity.py
python scripts/test-enterprise-tokens.py
python scripts/test-release-v1.py
```

The full repository test workflow additionally runs Python regression tests and Playwright browser smoke tests.
