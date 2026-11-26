---
name: sprite-pipeline
description: "Trigger: sprite, pixel art, Aseprite, sprite sheet, animation, reference fidelity. Run the canonical Sprite Foundry workflow."
license: Apache-2.0
metadata:
  author: marcos-Nieves-24
  version: "1.0"
---

## Activation Contract

Load this skill before creating, editing, exporting, reviewing or publishing any sprite.

## Hard Rules

- Treat `sprites/README.md` and `sprites/manifest.json` as canonical.
- Keep editable sources under `sprites/source/`; never hand-edit generated exports.
- Register every reference in `sprites/references/SOURCES.md`.
- Do not copy or downscale a reference render into a final sprite unless its license permits derivation and the spec records it.
- Run `doctor`, `verify`, `export` and `contact_sheet` through `tools/sprites/`.
- Do not mark an asset `approved` without visual review.
- Do not reference prototype or rejected assets from the root README.
- Do not commit, push or merge without explicit user authorization.

## Decision Gates

| Situation | Action |
| --- | --- |
| New asset | Add manifest entry, spec, palette and source registry record before drawing |
| Existing asset | Read its spec and proof; change only the source |
| Export requested | Run deterministic export, then contact sheet and verify |
| Visual rejection | Set status `rejected`; preserve evidence; do not silently replace it |
| Publication requested | Require status `approved` and a passing proof record |

## Execution Steps

1. Run `python3 tools/sprites/doctor.py`.
2. Read the asset spec, manifest entry and reference registry.
3. Edit the saved Aseprite source with stable layers and tagged animation.
4. Run `python3 tools/sprites/export.py <asset-id>`.
5. Run `python3 tools/sprites/contact_sheet.py <asset-id>`.
6. Review native 1x, scaled preview, dark/light sheet and filmstrip.
7. Run `python3 tools/sprites/verify.py <asset-id>`.
8. Update status only after the required review.

## Output Contract

Return the asset id, status, commands run, observed results, proof path, visual findings and unresolved decisions.

## References

- `../../sprites/README.md`
- `../../sprites/references/SOURCES.md`
- `../../tools/sprites/common.py`
