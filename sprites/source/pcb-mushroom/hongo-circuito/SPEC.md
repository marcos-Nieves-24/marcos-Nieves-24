# Hongo Circuito spec

Status: prototype

Reference: `user-hongo-circuito`

Native canvas: 384×256

Palette: `sprites/palettes/hongo-circuito.gpl` (64 colours)

Animation: `charge-cycle`, 4 frames

## Outcome

Reinterpret the complete reference as a hand-authored pixel sprite: wide purple mushroom, magenta/yellow fissures, orange gills, luminous roots, cyan PCB and navy background. Omit the battery.

## Fidelity rubric

| Dimension | Pass condition |
| --- | --- |
| Composition | 3:2 landscape, centered wide mushroom, PCB occupying the lower third |
| Silhouette | Mushroom reads at 1x without colour |
| Palette | Purple cap, warm gills, pink roots and cyan traces remain distinct |
| Detail | Fissures, gill fan, root branches, chips and vias survive 2x preview |
| Animation | Energy pulses without geometry drift; loop closes cleanly |
| Technical | Required layers/tags, 64-colour palette, valid atlas and integer export scale |

## Layer contract

`background`, `halo`, `pcb`, `traces`, `roots`, `stem`, `gills`, `cap`, `veins`, `details`, `energy`.

## Non-goals

- No battery icon or lightning bolt.
- No copied or downscaled reference pixels.
- No root README integration while status is `prototype`.
- No new robot, character or scenery outside the reference.
