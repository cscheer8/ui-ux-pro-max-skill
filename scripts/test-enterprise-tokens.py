#!/usr/bin/env python3
"""Smoke-test inheritance, overrides, governance, migrations, and persisted files."""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "src" / "ui-ux-pro-max" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from brand_system import generate_brand_system
from enterprise_tokens import deep_merge, export_enterprise_tokens


with tempfile.TemporaryDirectory() as tmp:
    result = generate_brand_system(
        "global logistics technology platform dependable clear scalable",
        "Atlas Group",
        output_format="markdown",
        persist=True,
        output_dir=tmp,
    )
    exported = export_enterprise_tokens(
        result["brand_system"],
        result["persistence"],
        child_brands=[{"name": "Atlas Europe", "primary": "#1144AA", "accent": "#EE9900"}],
        products=[{"name": "Atlas Dispatch", "brand": "Atlas Europe", "accent": "#00AA88"}],
        version="2.1.0",
        governance_status="review",
        owner="Enterprise Design Systems",
        approver="Design Council",
    )
    assert exported["status"] == "created"
    assert exported["validation"]["valid"]
    manifest = json.loads(Path(exported["manifest"]).read_text(encoding="utf-8"))
    assert manifest["token_version"] == "2.1.0"
    assert manifest["governance"]["status"] == "review"
    assert manifest["governance"]["approver"] == "Design Council"
    assert manifest["migrations"][0]["to"] == "2.1.0"
    child = manifest["brands"][0]
    product = manifest["products"][0]
    assert child["inheritance_chain"] == ["atlas-group", "atlas-europe"]
    assert product["inheritance_chain"] == ["atlas-group", "atlas-europe", "atlas-dispatch"]
    assert child["resolved_tokens"]["color"]["brand"]["primary"]["$value"] == "#1144AA"
    assert product["resolved_tokens"]["color"]["brand"]["primary"]["$value"] == "#1144AA"
    assert product["resolved_tokens"]["color"]["brand"]["accent"]["$value"] == "#00AA88"
    assert (Path(result["persistence"]["brand_system_dir"]) / "exports/enterprise-tokens/foundation.json").exists()
    assert deep_merge({"a": {"b": 1, "c": 2}}, {"a": {"b": 3}}) == {"a": {"b": 3, "c": 2}}

print("Enterprise token architecture smoke test passed.")
