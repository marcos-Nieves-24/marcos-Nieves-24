# Sprite Foundry pipeline

Objective: build a reproducible, professional sprite pipeline in the profile repository and prove it end to end with one PCB mushroom asset.
Branch: `feat/biopunk-pixel-readme`
Delivery strategy: local feature branch; commit `5ebe884` authorized; no push, PR, merge or root README integration without explicit authorization.
Test runner: `python3 -m unittest discover -s tools/sprites/tests -v`

## Specs

1. S1 — “arma un sistema para crear sprites profesional, no esa mamada.”
   - Acceptance: the repository has one canonical workflow, asset manifest, source registry, deterministic export commands, mechanical verification and proof records.
2. S2 — “Revisa que nos falta, que estamos haciendo con información de la web y arma propuesta para solucionarlo”
   - Acceptance: the implementation records authoritative web sources and converts them into local rules instead of ad hoc chat guidance.
3. S3 — “procede con la implementacion”
   - Acceptance: the first vertical slice is implemented and run locally, not only described.
4. S4 — “no quiero que uses el render original como tu evidencia. debe reinterpretar la imagen completa con fidelidad”
   - Acceptance: reference policy forbids using a reference render as final sprite pixels; the tracer bullet keeps a hand-authored source and records the reference as visual guidance only.
5. S5 — No commit, push, merge or root README integration without explicit authorization.
   - Acceptance: commit `5ebe884` was created after explicit authorization; no push, PR, merge or root README integration has occurred.
6. S6 — “continua con la siguiente fase”
   - Acceptance: review follow-ups are addressed for portable temporary directories, bounded subprocesses, atomic export rollback, clean CLI failures, malformed manifests, empty atlases and missing-file proofs; focused and full tests pass.

## Tasks

- T1 — Create canonical manifest, source registry, palette, spec and workflow docs. Route: inline. Status: completed.
- T2 — Implement `doctor`, `verify`, deterministic `export`, contact-sheet generation and unit tests. Route: inline. Status: completed.
- T3 — Migrate the hand-authored mushroom tracer bullet into canonical source/export paths and produce a proof record. Route: inline. Status: completed.
- T4 — Add the project `sprite-pipeline` skill and register the workflow in repository guidance. Route: inline. Status: completed.
- T5 — Harden export execution with portable temporary storage, subprocess timeouts and atomic rollback. Route: inline. Status: completed.
- T6 — Harden manifest, atlas, proof and CLI failure handling. Route: inline. Status: completed.
- T7 — Re-run full verification, review and commit the hardening slice. Route: inline. Status: pending.

## Log

- L1 — User requested a professional sprite creation system, an audit of missing capabilities and web information usage, and a proposal.
- L2 — User authorized implementation with “procede con la implementacion”.
- L3 — Existing evidence: 95 sprite files, 14 Aseprite sources, 14 JSON atlases, 5.7 MB, no scripts/CI/manifest/style guide/source registry, and no root README sprite references.
- L4 — Verified toolchain: Aseprite CLI 1.3.18.6-dev, Blender 5.3.0, Python 3.14.8, ImageMagick `identify`; Git LFS is not installed.
- L5 — Authoritative sources: Aseprite CLI, sprite-sheet, animation and color-mode docs; Lospec palette submission rules.
- L6 — Implemented `tools/sprites/` with doctor, deterministic export, contact sheets, verification and six unit tests. Migrated `hongo-circuito` to canonical source/export paths; proof record passes with zero findings.
- L7 — Verification evidence: unit tests 6/6, doctor pass, `verify.py --all` pass, skill structure pass, `git diff --check` pass. No commit, push, merge or root README integration.
- L8 — User authorized commits and the next phase with “continua con la siguiente fase”.
- L9 — Isolated Gentle AI build `423d90a` fixed the OpenCode relay. `R4-verify-proof-on-failure` was corrected with observed RED to GREEN; 7/7 tests passed. Lineage `review-e09561fcec56f698` was acknowledged and commit `5ebe884` created.
- L10 — Committed-only lineage `review-4a962e591f3f842b` was approved and acknowledged. Its non-blocking resilience, reliability and readability advisories define the T5-T6 hardening scope.
- L11 — T5-T6 implemented with observed RED to GREEN. Full suite 19/19, doctor and `verify.py --all --check-only` pass. Differential checks for doctor, verify, export and contact-sheet match commit `5ebe884`; all seven generated artifacts are byte-identical.
