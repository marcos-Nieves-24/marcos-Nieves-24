#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SpriteError, get_asset, load_manifest, validate_asset, write_proof  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify one or all Sprite Foundry assets.")
    parser.add_argument("asset", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--check-only", action="store_true", help="Do not write proof records.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.asset and not args.all:
        parser.error("Provide an asset id or --all")

    try:
        manifest = load_manifest()
        assets = manifest["assets"] if args.all else [get_asset(args.asset, manifest)]
        results = []
        for asset in assets:
            findings = validate_asset(REPO_ROOT, asset)
            proof = None if args.check_only else write_proof(REPO_ROOT, asset, findings)
            results.append({"asset": asset["id"], "result": "pass" if not findings else "fail", "findings": findings, "proof": str(proof) if proof else None})
    except (SpriteError, json.JSONDecodeError) as exc:
        print(f"verify: {exc}", file=sys.stderr)
        return 2

    ok = all(result["result"] == "pass" for result in results)
    if args.json:
        print(json.dumps({"result": "pass" if ok else "fail", "assets": results}, indent=2))
    else:
        for result in results:
            print(f"{result['asset']}: {result['result']}")
            for finding in result["findings"]:
                print(f"  [{finding['severity']}] {finding['code']}: {finding['message']}")
            if result["proof"]:
                print(f"  proof: {result['proof']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
