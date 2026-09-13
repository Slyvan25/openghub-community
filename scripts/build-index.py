#!/usr/bin/env python3
"""Validates every profile under profiles/ and (re)generates index.json.

Mirrors the checks OpenGHub applies on import, so a file that passes here will
import cleanly. Run with --check to validate without writing.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "profiles"
FORMAT = 1
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(path, msg):
    print(f"  {path.relative_to(ROOT)}: {msg}")
    return False


def validate(path, data):
    ok = True
    if data.get("format") != FORMAT:
        ok = fail(path, f"format must be {FORMAT}")
    pid = data.get("id", "")
    if not ID_RE.match(pid) or len(pid) > 80:
        ok = fail(path, "id must be lowercase kebab-case")
    if not str(data.get("name", "")).strip() or len(data["name"]) > 80:
        ok = fail(path, "name is missing or too long")
    if not str(data.get("author", "")).strip():
        ok = fail(path, "author is missing")
    if data.get("license", "CC0-1.0") != "CC0-1.0":
        ok = fail(path, "license must be CC0-1.0")
    dev = data.get("device") or {}
    if not dev.get("modelId"):
        ok = fail(path, "device.modelId is missing")
    if path.parent.name != dev.get("modelId"):
        ok = fail(path, f"file must live under profiles/{dev.get('modelId')}/")
    if not isinstance(dev.get("productIds", []), list) or not dev.get("productIds"):
        ok = fail(path, "device.productIds must list at least one product id")
    prof = data.get("profile") or {}
    dpi = prof.get("dpiStages", [])
    if len(dpi) > 5 or any(not isinstance(d, int) or d <= 0 or d > 50000 for d in dpi):
        ok = fail(path, "dpiStages out of range")
    macros = prof.get("macros", [])
    if len(macros) > 64 or any(len(m.get("steps", [])) > 512 for m in macros):
        ok = fail(path, "too many macros or macro too long")
    return ok


def main():
    check_only = "--check" in sys.argv
    entries, ok, seen = [], True, set()
    for path in sorted(PROFILES.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            ok = fail(path, f"not valid JSON: {e}")
            continue
        if not validate(path, data):
            ok = False
            continue
        if data["id"] in seen:
            ok = fail(path, f"duplicate id {data['id']}")
            continue
        seen.add(data["id"])
        prof = data.get("profile") or {}
        entries.append({
            "id": data["id"],
            "name": data["name"],
            "author": data["author"],
            "description": data.get("description", ""),
            "device": data["device"],
            "application": data.get("application"),
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "macroCount": len(prof.get("macros", [])),
            "assignmentCount": len(prof.get("assignments", [])),
            "dpiStages": prof.get("dpiStages", []),
            "hasLighting": bool(prof.get("lightingZones")) or bool(prof.get("lighting")),
            "updated": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).date().isoformat(),
        })

    print(f"{len(entries)} valid profile(s)" + ("" if ok else " — with errors above"))
    if not ok:
        sys.exit(1)
    if check_only:
        return
    index = {
        "version": 1,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "profiles": entries,
    }
    (ROOT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print("index.json written")


if __name__ == "__main__":
    main()
