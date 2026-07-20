#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brand consistency auditing for persisted brand systems."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

AUDIT_EXTENSIONS = {".css", ".scss", ".sass", ".less", ".html", ".md", ".svg", ".js", ".jsx", ".ts", ".tsx", ".json"}
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\b")
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}{]+)", re.IGNORECASE)


def _flatten_token_values(value) -> list[str]:
    values: list[str] = []
    if isinstance(value, dict):
        if "$value" in value:
            token_value = value["$value"]
            if isinstance(token_value, str):
                values.append(token_value)
            elif isinstance(token_value, list):
                values.extend(str(item) for item in token_value)
        for child in value.values():
            values.extend(_flatten_token_values(child))
    elif isinstance(value, list):
        for child in value:
            values.extend(_flatten_token_values(child))
    return values


def _iter_auditable_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in AUDIT_EXTENSIONS:
            yield root
        return
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in AUDIT_EXTENSIONS:
            continue
        if any(part in {".git", "node_modules", "dist", "build", ".next", "coverage"} for part in path.parts):
            continue
        yield path


def _issue(code: str, severity: str, message: str, path: Path | None = None, value: str | None = None) -> dict:
    issue = {"code": code, "severity": severity, "message": message}
    if path is not None:
        issue["path"] = str(path)
    if value is not None:
        issue["value"] = value
    return issue


def _required_artifacts(brand_dir: Path) -> list[Path]:
    return [
        brand_dir / "MASTER.md",
        brand_dir / "brand-system.json",
        brand_dir / "tokens" / "semantic-brand-tokens.json",
        brand_dir / "assets" / "logo-brief.md",
    ]


def audit_brand_system(brand_system: dict, persistence: dict | None, target_path: str, write_report: bool = True) -> dict:
    """Audit a project directory against one persisted brand system."""
    if not persistence or not persistence.get("brand_system_dir"):
        return {"status": "skipped", "message": "Brand system must be persisted before auditing."}

    brand_dir = Path(persistence["brand_system_dir"]).resolve()
    target = Path(target_path).expanduser().resolve()
    if not target.exists():
        return {"status": "error", "message": f"Audit target does not exist: {target}"}

    tokens = brand_system.get("semantic_tokens", {})
    token_values = _flatten_token_values(tokens)
    approved_colors = {value.upper() for value in token_values if isinstance(value, str) and HEX_COLOR.fullmatch(value)}
    approved_colors.update({"#FFFFFF", "#000000"})
    approved_fonts = {
        value.strip().strip("'\"").lower()
        for value in token_values
        if isinstance(value, str) and not value.startswith("#") and not value.startswith("{")
    }

    issues: list[dict] = []
    scanned_files = 0
    discovered_colors: set[str] = set()
    discovered_fonts: set[str] = set()

    for required in _required_artifacts(brand_dir):
        if not required.exists():
            issues.append(_issue("missing-brand-artifact", "error", f"Missing required brand artifact: {required.name}", required))

    for path in _iter_auditable_files(target):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            issues.append(_issue("unreadable-file", "warning", "File could not be read during audit.", path))
            continue
        scanned_files += 1
        for color in HEX_COLOR.findall(text):
            normalized = color.upper()
            discovered_colors.add(normalized)
            if normalized not in approved_colors:
                issues.append(_issue("unapproved-color", "warning", "Color is not present in the semantic brand tokens.", path, normalized))
        for declaration in FONT_FAMILY.findall(text):
            for raw_font in declaration.split(","):
                font = raw_font.strip().strip("'\"").lower()
                if not font or font in {"inherit", "initial", "unset", "system-ui", "sans-serif", "serif", "monospace"}:
                    continue
                discovered_fonts.add(font)
                if approved_fonts and font not in approved_fonts:
                    issues.append(_issue("unapproved-font", "warning", "Font family is not present in the brand typography tokens.", path, font))

    source_tokens = brand_dir / "tokens" / "semantic-brand-tokens.json"
    exported_json = brand_dir / "exports" / "json" / "semantic-brand-tokens.json"
    if exported_json.exists() and source_tokens.exists():
        try:
            if json.loads(exported_json.read_text(encoding="utf-8")) != json.loads(source_tokens.read_text(encoding="utf-8")):
                issues.append(_issue("token-export-drift", "error", "Production JSON token export does not match the semantic token source.", exported_json))
        except json.JSONDecodeError:
            issues.append(_issue("invalid-token-json", "error", "Token JSON could not be parsed.", exported_json))

    unique_issues = []
    seen = set()
    for issue in issues:
        signature = (issue["code"], issue.get("path"), issue.get("value"))
        if signature not in seen:
            seen.add(signature)
            unique_issues.append(issue)
    issues = unique_issues

    counts = {
        "error": sum(issue["severity"] == "error" for issue in issues),
        "warning": sum(issue["severity"] == "warning" for issue in issues),
        "info": sum(issue["severity"] == "info" for issue in issues),
    }
    score = max(0, 100 - counts["error"] * 20 - counts["warning"] * 5 - counts["info"])
    report = {
        "status": "completed",
        "project_name": brand_system.get("project_name", "Brand"),
        "brand_system_dir": str(brand_dir),
        "target_path": str(target),
        "score": score,
        "summary": counts,
        "scanned_files": scanned_files,
        "approved_colors": sorted(approved_colors),
        "discovered_colors": sorted(discovered_colors),
        "discovered_fonts": sorted(discovered_fonts),
        "issues": issues,
    }

    if write_report:
        audit_dir = brand_dir / "audits"
        audit_dir.mkdir(parents=True, exist_ok=True)
        json_path = audit_dir / "brand-audit.json"
        md_path = audit_dir / "brand-audit.md"
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        md_path.write_text(_format_markdown(report), encoding="utf-8")
        report["created_files"] = [str(json_path.relative_to(brand_dir)), str(md_path.relative_to(brand_dir))]
    return report


def _format_markdown(report: dict) -> str:
    lines = [
        f"# {report['project_name']} — Brand Consistency Audit",
        "",
        f"- **Score:** {report['score']}/100",
        f"- **Files scanned:** {report['scanned_files']}",
        f"- **Errors:** {report['summary']['error']}",
        f"- **Warnings:** {report['summary']['warning']}",
        "",
        "## Findings",
        "",
    ]
    if not report["issues"]:
        lines.append("No consistency issues were detected.")
    else:
        for issue in report["issues"]:
            location = f" — `{issue['path']}`" if issue.get("path") else ""
            value = f" (`{issue['value']}`)" if issue.get("value") else ""
            lines.append(f"- **{issue['severity'].upper()} · {issue['code']}**: {issue['message']}{value}{location}")
    lines.extend([
        "",
        "## Approved Colors",
        "",
        *[f"- `{color}`" for color in report["approved_colors"]],
        "",
    ])
    return "\n".join(lines)
