#!/usr/bin/env python3
"""Smoke tests for provider-backed image generation without network calls."""

import base64
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "src" / "ui-ux-pro-max" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from brand_system import generate_brand_system
from image_execution import GeneratedImage, execute_image_generation

# Valid 1x1 transparent PNG.
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class FlakyFakeProvider:
    name = "deterministic-test"

    def __init__(self):
        self.calls = 0

    def generate(self, *, prompt, negative_prompt, model, size, quality, output_format):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("simulated transient provider failure")
        return GeneratedImage(
            data=PNG_BYTES,
            provider=self.name,
            model=model,
            output_format=output_format,
            revised_prompt=f"TEST: {prompt[:40]}",
            provider_request_id=f"fake-{self.calls}",
            usage={"total_tokens": 1},
        )


def main() -> int:
    result = generate_brand_system(
        "regional logistics company dependable clear modern",
        "Northstar Transit",
        output_format="json",
        persist=False,
    )
    system = result["brand_system"]

    with tempfile.TemporaryDirectory() as temp_dir:
        brand_dir = Path(temp_dir) / "brand-system" / "northstar-transit"
        brand_dir.mkdir(parents=True)
        persistence = {"status": "created", "brand_system_dir": str(brand_dir)}
        provider = FlakyFakeProvider()

        first = execute_image_generation(
            system,
            persistence,
            provider=provider,
            image_types=["logo"],
            model="test-image-model",
            size="1024x1024",
            quality="low",
            output_format="png",
            attempts=2,
        )
        if first["status"] != "created" or provider.calls != 2:
            raise AssertionError("Retry flow did not recover from the simulated provider failure")
        first_record = first["assets"][0]
        first_path = brand_dir / first_record["file"]
        if first_path.read_bytes() != PNG_BYTES:
            raise AssertionError("Generated image bytes were not persisted correctly")
        if first_record["sha256"] != hashlib.sha256(PNG_BYTES).hexdigest():
            raise AssertionError("Generated image hash is incorrect")
        if first_record["provider"] != "deterministic-test" or first_record["provider_request_id"] != "fake-2":
            raise AssertionError("Provider provenance was not recorded")

        second = execute_image_generation(
            system,
            persistence,
            provider=provider,
            image_types=["imagery"],
            model="test-image-model",
            size="1536x1024",
            quality="medium",
            output_format="png",
            attempts=1,
            regenerate_from=first_record["asset_id"],
        )
        second_record = second["assets"][0]
        if second_record["regenerates"] != first_record["asset_id"]:
            raise AssertionError("Regeneration lineage was not recorded")

        manifest_path = brand_dir / "assets" / "generated" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if len(manifest["assets"]) != 2:
            raise AssertionError("Manifest should preserve append-only generation history")
        if manifest["assets"][0]["asset_type"] != "logo" or manifest["assets"][1]["asset_type"] != "imagery":
            raise AssertionError("Manifest asset order or types are incorrect")

        skipped = execute_image_generation(
            system,
            {"status": "skipped_exists", "brand_system_dir": str(brand_dir)},
            provider=provider,
            image_types=["logo"],
        )
        if skipped["status"] != "skipped":
            raise AssertionError("Execution should not modify a persistence run that was skipped")

    print("Executed image generation smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
