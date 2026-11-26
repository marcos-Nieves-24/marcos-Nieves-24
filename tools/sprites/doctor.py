#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import MANIFEST_PATH, SpriteError, run  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Sprite Foundry preconditions without changing files.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    checks = []

    def check(name: str, ok: bool, detail: str, fix: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail, "fix": fix})

    for command in ("python3", "aseprite", "identify"):
        path = shutil.which(command)
        check(command, path is not None, path or "not found", f"Install {command} and put it on PATH.")

    try:
        version = run(["aseprite", "--version"]).stdout.strip()
        check("aseprite-version", True, version)
    except SpriteError as exc:
        check("aseprite-version", False, str(exc), "Fix the Aseprite CLI installation.")

    check("pillow", importlib.util.find_spec("PIL") is not None, "Pillow Python package", "Install Pillow: python3 -m pip install pillow")
    check("manifest", MANIFEST_PATH.is_file(), str(MANIFEST_PATH), "Create sprites/manifest.json.")
    check("source-registry", (REPO_ROOT / "sprites/references/SOURCES.md").is_file(), "sprites/references/SOURCES.md", "Create the source registry.")

    ok = all(item["ok"] for item in checks)
    payload = {"result": "pass" if ok else "fail", "checks": checks}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for item in checks:
            print(f"{'PASS' if item['ok'] else 'FAIL'} {item['name']}: {item['detail']}")
            if not item["ok"] and item["fix"]:
                print(f"  fix: {item['fix']}")
        print(f"doctor: {'pass' if ok else 'fail'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
