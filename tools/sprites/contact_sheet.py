#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SpriteError, contact_sheet, get_asset, load_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate dark/light contact sheets and a filmstrip.")
    parser.add_argument("asset")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = contact_sheet(REPO_ROOT, get_asset(args.asset, load_manifest()))
    except SpriteError as exc:
        print(f"contact-sheet: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.json else f"generated previews for {result['asset']}: {', '.join(result['outputs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
