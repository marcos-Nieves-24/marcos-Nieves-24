# Repository guidance

## Sprite work

- Load `skills/sprite-pipeline/SKILL.md` before any sprite task.
- Treat `sprites/README.md` and `sprites/manifest.json` as the canonical workflow.
- Run `python3 tools/sprites/doctor.py` before editing or exporting sprites.
- Keep editable sources under `sprites/source/` and generated files under `sprites/export/`.
- Never hand-edit generated exports or use a reference render as final sprite pixels.
- Require a passing proof record and `approved` status before root README integration.
- Do not commit, push or merge without explicit user authorization.
