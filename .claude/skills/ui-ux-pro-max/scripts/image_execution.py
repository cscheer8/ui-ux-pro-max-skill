#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Execute brand image prompts through pluggable providers and persist outputs."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from asset_generation import build_asset_package

SUPPORTED_IMAGE_TYPES = ("logo", "icon_system", "imagery", "social_kit")
SUPPORTED_OUTPUT_FORMATS = ("png", "webp", "jpeg")
SUPPORTED_SIZES = ("1024x1024", "1024x1536", "1536x1024", "auto")
SUPPORTED_QUALITIES = ("low", "medium", "high", "auto")


@dataclass(frozen=True)
class GeneratedImage:
    data: bytes
    provider: str
    model: str
    output_format: str
    revised_prompt: str | None = None
    provider_request_id: str | None = None
    usage: dict | None = None


class ImageProvider(Protocol):
    name: str

    def generate(
        self,
        *,
        prompt: str,
        negative_prompt: str,
        model: str,
        size: str,
        quality: str,
        output_format: str,
    ) -> GeneratedImage:
        """Generate one image and return its bytes and provenance metadata."""


class OpenAIImageProvider:
    """OpenAI Images API adapter using only the Python standard library."""

    name = "openai"

    def __init__(self, api_key: str | None = None, timeout: int = 180) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for --image-provider openai")

    def generate(
        self,
        *,
        prompt: str,
        negative_prompt: str,
        model: str,
        size: str,
        quality: str,
        output_format: str,
    ) -> GeneratedImage:
        combined_prompt = prompt
        if negative_prompt:
            combined_prompt += f"\nAvoid: {negative_prompt}."
        payload = {
            "model": model,
            "prompt": combined_prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            "output_format": output_format,
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/images/generations",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "ui-ux-pro-max-skill/brand-image-executor",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
                request_id = response.headers.get("x-request-id")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI image generation failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenAI image generation connection failed: {exc.reason}") from exc

        items = body.get("data") or []
        if not items or not items[0].get("b64_json"):
            raise RuntimeError("OpenAI image generation returned no base64 image data")
        item = items[0]
        return GeneratedImage(
            data=base64.b64decode(item["b64_json"]),
            provider=self.name,
            model=model,
            output_format=output_format,
            revised_prompt=item.get("revised_prompt"),
            provider_request_id=request_id,
            usage=body.get("usage"),
        )


def get_provider(name: str) -> ImageProvider:
    if name == "openai":
        return OpenAIImageProvider()
    raise ValueError(f"Unsupported image provider: {name}")


def execute_image_generation(
    system: dict,
    persistence: dict,
    *,
    provider: ImageProvider,
    image_types: list[str],
    model: str = "gpt-image-1",
    size: str = "1024x1024",
    quality: str = "auto",
    output_format: str = "png",
    attempts: int = 3,
    regenerate_from: str | None = None,
) -> dict:
    """Generate and persist finished image assets plus an append-only manifest."""
    if not persistence or persistence.get("status") not in {"created", "overwritten"}:
        return {
            "status": "skipped",
            "created_files": [],
            "message": "Image execution requires a newly created or overwritten persistent brand package.",
        }
    unknown = [item for item in image_types if item not in SUPPORTED_IMAGE_TYPES]
    if unknown:
        raise ValueError(f"Unsupported image type(s): {', '.join(unknown)}")
    if output_format not in SUPPORTED_OUTPUT_FORMATS:
        raise ValueError(f"Unsupported image format: {output_format}")
    if size not in SUPPORTED_SIZES:
        raise ValueError(f"Unsupported image size: {size}")
    if quality not in SUPPORTED_QUALITIES:
        raise ValueError(f"Unsupported image quality: {quality}")
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    brand_dir = Path(persistence["brand_system_dir"])
    generated_dir = brand_dir / "assets" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = generated_dir / "manifest.json"
    manifest = _read_manifest(manifest_path, system["project_name"])
    prompts = build_asset_package(system)["generation_prompts"]
    created_files: list[str] = []
    records: list[dict] = []

    for image_type in image_types:
        prompt_spec = prompts[image_type]
        result = _generate_with_retry(
            provider,
            prompt=prompt_spec["prompt"],
            negative_prompt=prompt_spec.get("negative_prompt", ""),
            model=model,
            size=size,
            quality=quality,
            output_format=output_format,
            attempts=attempts,
        )
        now = datetime.now(timezone.utc)
        digest = hashlib.sha256(result.data).hexdigest()
        asset_id = f"{image_type}-{now.strftime('%Y%m%dT%H%M%SZ')}-{digest[:10]}"
        category_dir = generated_dir / image_type.replace("_", "-")
        category_dir.mkdir(parents=True, exist_ok=True)
        path = category_dir / f"{asset_id}.{result.output_format}"
        path.write_bytes(result.data)
        relative_path = str(path.relative_to(brand_dir))
        record = {
            "asset_id": asset_id,
            "asset_type": image_type,
            "file": relative_path,
            "sha256": digest,
            "bytes": len(result.data),
            "created_at": now.isoformat(),
            "provider": result.provider,
            "model": result.model,
            "size": size,
            "quality": quality,
            "output_format": result.output_format,
            "prompt": prompt_spec["prompt"],
            "negative_prompt": prompt_spec.get("negative_prompt", ""),
            "revised_prompt": result.revised_prompt,
            "provider_request_id": result.provider_request_id,
            "usage": result.usage,
            "regenerates": regenerate_from,
        }
        manifest["assets"].append(record)
        created_files.append(relative_path)
        records.append(record)

    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    created_files.append(str(manifest_path.relative_to(brand_dir)))
    return {
        "status": "created",
        "provider": provider.name,
        "created_files": created_files,
        "assets": records,
        "manifest": str(manifest_path),
    }


def _generate_with_retry(provider: ImageProvider, *, attempts: int, **kwargs) -> GeneratedImage:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return provider.generate(**kwargs)
        except Exception as exc:  # provider failures are retried as a unit
            last_error = exc
            if attempt < attempts:
                time.sleep(min(2 ** (attempt - 1), 4))
    raise RuntimeError(f"Image generation failed after {attempts} attempt(s): {last_error}") from last_error


def _read_manifest(path: Path, project_name: str) -> dict:
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and isinstance(payload.get("assets"), list):
                return payload
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "schema_version": "1.0.0",
        "project": project_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": None,
        "assets": [],
    }
