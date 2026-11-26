# Sprite Foundry

Canonical workflow for profile sprites. Sources are editable Aseprite files; exports are generated; proofs record what was checked.

## Layout

```text
sprites/
  manifest.json
  references/SOURCES.md
  palettes/
  source/<family>/<asset>/SPEC.md
  source/<family>/<asset>/*.aseprite
  export/<family>/<asset>/
  proofs/<asset>.json
  rejected/
```

Legacy prototype directories remain outside the canonical path until migrated or quarantined.

## Commands

```bash
python3 tools/sprites/doctor.py
python3 tools/sprites/verify.py hongo-circuito
python3 tools/sprites/export.py hongo-circuito
python3 tools/sprites/contact_sheet.py hongo-circuito
python3 -m unittest discover -s tools/sprites/tests -v
```

Run `doctor` first. Run `verify` after every source change. Run `export` only from a saved `.aseprite` source. Run `contact_sheet` after export.

## Lifecycle

`concept → prototype → review → approved` or `rejected`.

Only `approved` assets may be referenced by the root README. A green mechanical check does not imply visual approval.

## Definition of done

- Manifest, spec, palette and source registry are present.
- Required layers and animation tags exist.
- Palette, alpha, dimensions, frame timing and atlas metadata pass verification.
- Native 1x, scaled preview, dark/light contact sheet and filmstrip are reviewed.
- A proof record exists.
- The asset status is explicitly `approved` before publication.

## Reference policy

References guide composition and style. They are not copied or downscaled into final sprites unless the license allows derivation and the spec records it. Web guidance must be registered in `references/SOURCES.md` before it becomes a local rule.
