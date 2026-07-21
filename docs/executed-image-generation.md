# Executed AI Image Generation

The Brand System Extension separates two different operations:

- `--generate-assets` creates briefs, prompts, and editable templates without calling an external provider.
- `--render-assets` calls a configured image provider and saves finished image files.

This distinction prevents prompt generation from being mistaken for completed visual generation.

## OpenAI provider setup

Set an OpenAI API key in the environment:

### macOS or Linux

```bash
export OPENAI_API_KEY="your-key"
```

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY="your-key"
```

Do not commit API keys to the repository or place them inside a generated brand package.

## Generate finished assets

```bash
python src/ui-ux-pro-max/scripts/search.py \
  "regional transit brand dependable clear modern" \
  --brand-system \
  --persist \
  --render-assets \
  --image-provider openai \
  --image-types logo,imagery,social_kit \
  -p "Northstar Transit" \
  --output-dir "."
```

`--render-assets` automatically enables the provider-neutral briefs and prompts so the finished files remain connected to their design direction.

## Output

```text
brand-system/<project>/assets/generated/
├── logo/
│   └── logo-<timestamp>-<hash>.png
├── imagery/
│   └── imagery-<timestamp>-<hash>.png
├── social-kit/
│   └── social_kit-<timestamp>-<hash>.png
└── manifest.json
```

The append-only manifest records:

- Asset ID and category
- Relative file path
- SHA-256 hash and byte count
- Provider and model
- Size, quality, and output format
- Original and negative prompts
- Provider-revised prompt when returned
- Provider request ID and usage metadata when returned
- Regeneration lineage
- UTC creation timestamp

## Asset types

- `logo`
- `icon_system`
- `imagery`
- `social_kit`

Use a comma-separated list with `--image-types`. Hyphenated `icon-system` and `social-kit` input is normalized automatically.

## Generation settings

```text
--image-model gpt-image-1
--image-size 1024x1024|1024x1536|1536x1024|auto
--image-quality low|medium|high|auto
--image-format png|webp|jpeg
--image-attempts 3
```

The executor retries transient provider failures using bounded exponential backoff.

## Regeneration history

To identify a new asset as a regeneration of an earlier result, pass the previous manifest asset ID:

```bash
python src/ui-ux-pro-max/scripts/search.py \
  "regional transit brand dependable clear modern" \
  --brand-system \
  --persist \
  --force \
  --render-assets \
  --image-types logo \
  --regenerate-from "logo-20260101T120000Z-abc1234567" \
  -p "Northstar Transit" \
  --output-dir "."
```

The relationship is stored in the new manifest record under `regenerates`.

## Cost and safety boundary

`--complete-brand-package` does not automatically call a paid image provider. External generation occurs only when `--render-assets` is explicitly supplied.
