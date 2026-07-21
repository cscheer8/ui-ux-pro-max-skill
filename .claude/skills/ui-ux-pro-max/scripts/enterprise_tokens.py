#!/usr/bin/env python3
"""Create versioned multi-brand token architectures with deterministic inheritance."""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "brand"


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge mappings; scalar and token nodes are replaced by overrides."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict) and "$value" not in value:
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _token(value: str, token_type: str = "color") -> dict:
    return {"$value": value, "$type": token_type}


def _brand_override(primary: str | None, accent: str | None) -> dict:
    override: dict = {}
    if primary or accent:
        override = {"color": {"brand": {}}}
        if primary:
            override["color"]["brand"]["primary"] = _token(primary)
        if accent:
            override["color"]["brand"]["accent"] = _token(accent)
    return override


def validate_architecture(payload: dict) -> dict:
    errors: list[str] = []
    ids: set[str] = set()
    for collection in ("brands", "products"):
        for item in payload.get(collection, []):
            item_id = item.get("id")
            if not item_id or item_id in ids:
                errors.append(f"duplicate or missing id: {item_id}")
            ids.add(item_id)
            if not isinstance(item.get("resolved_tokens"), dict):
                errors.append(f"{item_id}: missing resolved_tokens")
            if not item.get("inheritance_chain"):
                errors.append(f"{item_id}: missing inheritance_chain")
    governance = payload.get("governance", {})
    if governance.get("status") not in {"draft", "review", "approved", "deprecated"}:
        errors.append("invalid governance status")
    return {"valid": not errors, "errors": errors, "node_count": len(ids)}


def export_enterprise_tokens(
    system: dict,
    persistence: dict,
    *,
    child_brands: list[dict],
    products: list[dict],
    version: str = "1.0.0",
    governance_status: str = "draft",
    owner: str = "Design Systems Team",
    approver: str | None = None,
) -> dict:
    if not persistence or persistence.get("status") not in {"created", "overwritten"}:
        return {"status": "skipped", "created_files": [], "message": "Enterprise token export requires a writable persisted brand package."}

    brand_dir = Path(persistence["brand_system_dir"])
    root = brand_dir / "exports" / "enterprise-tokens"
    root.mkdir(parents=True, exist_ok=True)
    parent_id = _slug(system["project_name"])
    foundation = copy.deepcopy(system["semantic_tokens"])

    resolved_brands: list[dict] = []
    brand_lookup = {parent_id: foundation}
    for spec in child_brands:
        child_id = _slug(spec["name"])
        overrides = deep_merge(spec.get("overrides", {}), _brand_override(spec.get("primary"), spec.get("accent")))
        resolved = deep_merge(foundation, overrides)
        brand_lookup[child_id] = resolved
        resolved_brands.append({
            "id": child_id,
            "name": spec["name"],
            "parent": parent_id,
            "inheritance_chain": [parent_id, child_id],
            "overrides": overrides,
            "resolved_tokens": resolved,
        })

    resolved_products: list[dict] = []
    for spec in products:
        product_id = _slug(spec["name"])
        parent_brand = _slug(spec.get("brand", parent_id))
        if parent_brand not in brand_lookup:
            raise ValueError(f"Unknown parent brand for product {spec['name']}: {parent_brand}")
        overrides = deep_merge(spec.get("overrides", {}), _brand_override(spec.get("primary"), spec.get("accent")))
        resolved = deep_merge(brand_lookup[parent_brand], overrides)
        chain = [parent_id] if parent_brand == parent_id else [parent_id, parent_brand]
        chain.append(product_id)
        resolved_products.append({
            "id": product_id,
            "name": spec["name"],
            "brand": parent_brand,
            "inheritance_chain": chain,
            "overrides": overrides,
            "resolved_tokens": resolved,
        })

    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "1.0.0",
        "token_version": version,
        "foundation": {"id": parent_id, "name": system["project_name"], "tokens": foundation},
        "brands": resolved_brands,
        "products": resolved_products,
        "governance": {
            "status": governance_status,
            "owner": owner,
            "approver": approver,
            "created_at": now,
            "updated_at": now,
            "approval_required_for": ["foundation", "brand-overrides", "breaking-migrations"],
        },
        "migrations": [{
            "from": None,
            "to": version,
            "type": "initial",
            "breaking": False,
            "notes": "Initial enterprise token architecture generated from the persisted semantic brand system.",
        }],
    }
    validation = validate_architecture(payload)
    if not validation["valid"]:
        raise ValueError("Enterprise token architecture failed validation: " + "; ".join(validation["errors"]))
    payload["validation"] = validation

    created: list[str] = []
    files = {
        "foundation.json": payload["foundation"],
        "governance.json": payload["governance"],
        "migrations.json": payload["migrations"],
        "enterprise-token-manifest.json": payload,
    }
    for item in resolved_brands:
        files[f"brands/{item['id']}.json"] = item
    for item in resolved_products:
        files[f"products/{item['id']}.json"] = item
    for relative, data in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        created.append(str(path.relative_to(brand_dir)))

    return {"status": "created", "created_files": created, "manifest": str(root / "enterprise-token-manifest.json"), "validation": validation}
