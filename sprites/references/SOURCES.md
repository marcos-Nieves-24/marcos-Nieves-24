# Sprite sources

Record every external reference before it influences an asset. A reference is guidance, not a source of final pixels, unless its license explicitly permits derivation and the asset spec records that derivation.

## User reference

| ID | Source | Author | License | Accessed | Allowed use | Modifications |
| --- | --- | --- | --- | --- | --- | --- |
| `user-hongo-circuito` | `sprites/referencias/hongo_circuito.png` | unknown | unknown | 2026-11-26 | Visual reference only; no pixels copied or downscaled into the final sprite | Battery omitted; composition, palette and detail reinterpreted |

## Authoritative technical sources

| ID | URL | Publisher | Accessed | Used for |
| --- | --- | --- | --- | --- |
| `aseprite-cli` | https://www.aseprite.org/docs/cli/ | Aseprite / Igara Studio | 2026-11-26 | Batch export, sheets, JSON data, tags, layers, padding, trim and extrude |
| `aseprite-sprite-sheet` | https://www.aseprite.org/docs/sprite-sheet/ | Aseprite / Igara Studio | 2026-11-26 | Sprite-sheet layout and frame selection |
| `aseprite-animation` | https://www.aseprite.org/docs/animation/ | Aseprite / Igara Studio | 2026-11-26 | Frames, cels, tags, duration, onion skinning and loops |
| `aseprite-color-mode` | https://www.aseprite.org/docs/color-mode/ | Aseprite / Igara Studio | 2026-11-26 | RGB versus indexed palettes and transparency semantics |
| `lospec-palette-rules` | https://lospec.com/palettes/submit | Lospec | 2026-11-26 | Cohesive ramps, unique colours, ordering and provenance |

## Policy

- Store the URL or local path, author, license, access date and intended use.
- Mark unknown metadata as `unknown`; never invent it.
- Keep generated concepts separate from hand-authored final sources.
- Do not use a reference render as evidence that a sprite is faithful.
- Re-check the source and license before publication or commercial use.
