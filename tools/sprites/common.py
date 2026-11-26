#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "sprites" / "manifest.json"
ALLOWED_STATUSES = {"concept", "prototype", "review", "approved", "rejected"}
REQUIRED_ASSET_FIELDS = {
    "id", "status", "source", "spec", "palette", "max_colors", "preview_scale",
    "native", "required_layers", "animation_tags", "exports",
}
REQUIRED_EXPORTS = {"png", "gif", "sheet", "atlas"}
COMMAND_TIMEOUT_SECONDS = 120


class SpriteError(RuntimeError):
    pass


def run(command: list[str], *, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        raise SpriteError(f"Command not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise SpriteError(f"Command timed out after {COMMAND_TIMEOUT_SECONDS}s: {' '.join(command)}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise SpriteError(f"Command failed: {' '.join(command)}\n{detail}") from exc


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    if not path.is_file():
        raise SpriteError(f"Manifest not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SpriteError(f"Invalid manifest JSON: {path}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise SpriteError("Manifest root must be an object")
    if data.get("schema_version") != 1:
        raise SpriteError("Unsupported manifest schema_version")
    assets = data.get("assets")
    if not isinstance(assets, list):
        raise SpriteError("Manifest assets must be a list")
    ids: list[str] = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise SpriteError(f"Manifest asset {index} must be an object")
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or not asset_id.strip():
            raise SpriteError(f"Manifest asset {index} has an invalid id")
        missing = sorted(REQUIRED_ASSET_FIELDS - set(asset))
        if missing:
            raise SpriteError(f"Manifest asset {asset_id} is missing required fields: {', '.join(missing)}")
        for field in ("source", "spec", "palette"):
            if not isinstance(asset[field], str) or not asset[field].strip():
                raise SpriteError(f"Manifest asset {asset_id} has an invalid {field}")
        for field in ("max_colors", "preview_scale"):
            value = asset[field]
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise SpriteError(f"Manifest asset {asset_id} has an invalid {field}")
        native = asset["native"]
        if not isinstance(native, dict) or any(
            not isinstance(native.get(dimension), int)
            or isinstance(native.get(dimension), bool)
            or native[dimension] <= 0
            for dimension in ("width", "height")
        ):
            raise SpriteError(f"Manifest asset {asset_id} has invalid native dimensions")
        for field in ("required_layers", "animation_tags"):
            value = asset[field]
            if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                raise SpriteError(f"Manifest asset {asset_id} has an invalid {field}")
            if field == "animation_tags" and not value:
                raise SpriteError(f"Manifest asset {asset_id} has no animation tags")
        exports = asset["exports"]
        if not isinstance(exports, dict) or any(
            not isinstance(exports.get(name), str) or not exports[name].strip()
            for name in REQUIRED_EXPORTS
        ):
            raise SpriteError(f"Manifest asset {asset_id} has invalid exports")
        ids.append(asset_id)
    if len(ids) != len(set(ids)):
        raise SpriteError("Manifest contains duplicate asset ids")
    for asset in assets:
        if asset.get("status") not in ALLOWED_STATUSES:
            raise SpriteError(f"Invalid status for {asset.get('id')}: {asset.get('status')}")
    return data


def get_asset(asset_id: str, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or load_manifest()
    for asset in manifest["assets"]:
        if asset["id"] == asset_id:
            return asset
    raise SpriteError(f"Unknown asset: {asset_id}")


def parse_gpl(path: Path) -> list[str]:
    if not path.is_file():
        raise SpriteError(f"Palette not found: {path}")
    colours: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "GIMP Palette", "Name:", "Columns:")):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            r, g, b = (int(part) for part in parts[:3])
        except ValueError:
            continue
        if not all(0 <= value <= 255 for value in (r, g, b)):
            raise SpriteError(f"Invalid GPL colour in {path}: {line}")
        colours.append(f"#{r:02x}{g:02x}{b:02x}")
    if not colours:
        raise SpriteError(f"Palette has no colours: {path}")
    if len(colours) != len(set(colours)):
        raise SpriteError(f"Palette contains duplicate colours: {path}")
    return colours


def aseprite_metadata(source: Path) -> tuple[list[str], list[str]]:
    layers = run(["aseprite", "-b", "--list-layers", str(source)]).stdout.splitlines()
    tags = run(["aseprite", "-b", "--list-tags", str(source)]).stdout.splitlines()
    return [line.strip() for line in layers if line.strip()], [line.strip() for line in tags if line.strip()]


def image_info(path: Path) -> list[dict[str, int]]:
    result = run(["identify", "-format", "%W %H %n %T\n", str(path)])
    frames: list[dict[str, int]] = []
    for line in result.stdout.splitlines():
        try:
            width, height, count, delay = (int(value) for value in line.split())
        except ValueError as exc:
            raise SpriteError(f"Unexpected identify output for {path}: {line}") from exc
        frames.append({"width": width, "height": height, "count": count, "delay": delay})
    if not frames:
        raise SpriteError(f"Image not readable: {path}")
    return frames


def atlas_frames(atlas: dict[str, Any]) -> list[dict[str, Any]]:
    frames = atlas.get("frames", [])
    if isinstance(frames, dict):
        return list(frames.values())
    return frames if isinstance(frames, list) else []


def validate_atlas_data(
    atlas: dict[str, Any],
    sheet_size: dict[str, int],
    native: dict[str, int],
    required_tags: list[str],
) -> list[str]:
    errors: list[str] = []
    meta = atlas.get("meta", {})
    declared_size = meta.get("size", {})
    expected_size = {"w": sheet_size["width"], "h": sheet_size["height"]}
    if declared_size != expected_size:
        errors.append(f"Atlas size {declared_size} does not match sheet {sheet_size}")
    frames = atlas_frames(atlas)
    if not frames:
        errors.append("Atlas has no frames")
    durations = [frame.get("duration") for frame in frames]
    if any(not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0 for duration in durations):
        errors.append("Frame durations must be positive integers")
    elif len(frames) > 1 and len(set(durations)) == 1:
        errors.append("Animated atlas uses uniform frame durations")
    tags = {tag.get("name") for tag in meta.get("frameTags", [])}
    missing_tags = sorted(set(required_tags) - tags)
    if missing_tags:
        errors.append(f"Missing animation tags: {', '.join(missing_tags)}")
    if native.get("width", 0) <= 0 or native.get("height", 0) <= 0:
        errors.append("Native dimensions must be positive")
    return errors


def validate_export_pixels(path: Path, palette: set[str]) -> list[str]:
    errors: list[str] = []
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        colours = rgba.getcolors(maxcolors=rgba.width * rgba.height)
        if colours is None:
            return [f"Could not enumerate colours in {path}"]
        for count, colour in colours:
            r, g, b, a = colour
            if a not in (0, 255):
                errors.append(f"Partial alpha pixel in {path}")
                break
        off_palette = sorted({f"#{r:02x}{g:02x}{b:02x}" for _, (r, g, b, a) in colours if a == 255} - palette)
        if off_palette:
            errors.append(f"Off-palette colours in {path}: {', '.join(off_palette[:6])}")
    return errors


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_asset(repo_root: Path, asset: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    def add(code: str, message: str, severity: str = "error") -> None:
        findings.append({"code": code, "severity": severity, "message": message})

    required = [asset["source"], asset["spec"], asset["palette"], *asset["exports"].values()]
    for relative in required:
        if not (repo_root / relative).is_file():
            add("missing_file", f"Missing required file: {relative}")

    if findings:
        return findings

    palette = parse_gpl(repo_root / asset["palette"])
    if len(palette) > asset["max_colors"]:
        add("palette_size", f"Palette has {len(palette)} colours; maximum is {asset['max_colors']}")

    layers, tags = aseprite_metadata(repo_root / asset["source"])
    missing_layers = sorted(set(asset["required_layers"]) - set(layers))
    if missing_layers:
        add("layers", f"Missing required layers: {', '.join(missing_layers)}")
    missing_tags = sorted(set(asset["animation_tags"]) - set(tags))
    if missing_tags:
        add("tags", f"Missing animation tags: {', '.join(missing_tags)}")

    scale = asset["preview_scale"]
    native = asset["native"]
    expected_size = {"width": native["width"] * scale, "height": native["height"] * scale}
    for key in ("png", "gif"):
        frames = image_info(repo_root / asset["exports"][key])
        for frame in frames:
            if {"width": frame["width"], "height": frame["height"]} != expected_size:
                add("export_size", f"{key.upper()} frame is {frame['width']}x{frame['height']}; expected {expected_size['width']}x{expected_size['height']}")
                break

    atlas = json.loads((repo_root / asset["exports"]["atlas"]).read_text(encoding="utf-8"))
    sheet_info = image_info(repo_root / asset["exports"]["sheet"])[0]
    sheet_size = {"width": sheet_info["width"], "height": sheet_info["height"]}
    for message in validate_atlas_data(atlas, sheet_size, native, asset["animation_tags"]):
        add("atlas", message)

    gif_frames = image_info(repo_root / asset["exports"]["gif"])
    if len(gif_frames) != len(atlas_frames(atlas)):
        add("frame_count", f"GIF has {len(gif_frames)} frames; atlas has {len(atlas_frames(atlas))}")

    palette_set = set(palette)
    for key in ("png", "sheet"):
        for message in validate_export_pixels(repo_root / asset["exports"][key], palette_set):
            add("pixels", message)

    return findings


def write_proof(repo_root: Path, asset: dict[str, Any], findings: list[dict[str, str]]) -> Path:
    proof_dir = repo_root / "sprites" / "proofs"
    proof_dir.mkdir(parents=True, exist_ok=True)
    files = [asset["source"], asset["spec"], asset["palette"], *asset["exports"].values()]
    proof = {
        "asset": asset["id"],
        "status": asset["status"],
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "result": "pass" if not findings else "fail",
        "findings": findings,
        "files": {
            relative: sha256(repo_root / relative) if (repo_root / relative).is_file() else None
            for relative in files
        },
    }
    path = proof_dir / f"{asset['id']}.json"
    path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    return path


def _replace_exports(pairs: list[tuple[Path, Path]], backup_dir: Path) -> None:
    staged: list[tuple[Path, Path]] = []
    backups: dict[Path, Path | None] = {}
    replaced: list[Path] = []
    try:
        for index, (generated, target) in enumerate(pairs):
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".new", dir=target.parent)
            os.close(descriptor)
            staged_path = Path(name)
            shutil.copy2(generated, staged_path)
            staged.append((staged_path, target))
            backup = backup_dir / f"backup-{index}"
            if target.exists():
                shutil.copy2(target, backup)
                backups[target] = backup
            else:
                backups[target] = None
        for staged_path, target in staged:
            os.replace(staged_path, target)
            replaced.append(target)
    except Exception as exc:
        for target in reversed(replaced):
            backup = backups[target]
            if backup is None:
                target.unlink(missing_ok=True)
            else:
                shutil.copy2(backup, target)
        if isinstance(exc, OSError):
            raise SpriteError(f"Could not replace export files: {exc}") from exc
        raise
    finally:
        for staged_path, _ in staged:
            staged_path.unlink(missing_ok=True)


def export_asset(repo_root: Path, asset: dict[str, Any]) -> dict[str, Any]:
    source = repo_root / asset["source"]
    export_dir = repo_root / Path(asset["exports"]["png"]).parent
    export_dir.mkdir(parents=True, exist_ok=True)
    scale = asset["preview_scale"]
    tag = asset["animation_tags"][0]
    with tempfile.TemporaryDirectory(prefix="sprite-foundry-") as temp:
        temp_dir = Path(temp)
        png = temp_dir / "preview.png"
        gif = temp_dir / "preview.gif"
        sheet = temp_dir / "sheet.png"
        atlas = temp_dir / "sheet.json"
        run(["aseprite", "-b", "--frame-range", "1,1", str(source), "--scale", str(scale), "--save-as", str(png)])
        run(["aseprite", "-b", "--tag", tag, str(source), "--scale", str(scale), "--save-as", str(gif)])
        run([
            "aseprite", "-b", str(source), "--sheet", str(sheet), "--data", str(atlas),
            "--shape-padding", "1", "--border-padding", "1", "--extrude", "--list-tags", "--list-layers",
        ])
        _replace_exports(
            [
                (png, repo_root / asset["exports"]["png"]),
                (gif, repo_root / asset["exports"]["gif"]),
                (sheet, repo_root / asset["exports"]["sheet"]),
                (atlas, repo_root / asset["exports"]["atlas"]),
            ],
            temp_dir,
        )
    return {"asset": asset["id"], "exported": list(asset["exports"].values())}


def contact_sheet(repo_root: Path, asset: dict[str, Any]) -> dict[str, Any]:
    sheet_path = repo_root / asset["exports"]["sheet"]
    atlas_path = repo_root / asset["exports"]["atlas"]
    output_dir = sheet_path.parent
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    frame_specs = atlas_frames(atlas)
    if not frame_specs:
        raise SpriteError(f"Atlas has no frames: {atlas_path}")
    frames = []
    with Image.open(sheet_path) as sheet:
        sheet = sheet.convert("RGBA")
        for frame in frame_specs:
            rect = frame["frame"]
            frames.append(sheet.crop((rect["x"], rect["y"], rect["x"] + rect["w"], rect["y"] + rect["h"])))

    gap = max(4, asset["native"]["width"] // 32)
    columns = math.ceil(math.sqrt(len(frames)))
    rows = math.ceil(len(frames) / columns)
    cell_w = max(frame.width for frame in frames)
    cell_h = max(frame.height for frame in frames)
    grid_w = columns * cell_w + (columns + 1) * gap
    grid_h = rows * cell_h + (rows + 1) * gap

    outputs = []
    for name, background in (("contact-dark.png", (5, 6, 17, 255)), ("contact-light.png", (244, 231, 197, 255))):
        canvas = Image.new("RGBA", (grid_w, grid_h), background)
        for index, frame in enumerate(frames):
            x = gap + (index % columns) * (cell_w + gap)
            y = gap + (index // columns) * (cell_h + gap)
            canvas.alpha_composite(frame, (x, y))
        path = output_dir / name
        canvas.convert("RGB").save(path)
        outputs.append(str(path.relative_to(repo_root)))

    filmstrip = Image.new("RGBA", (len(frames) * cell_w + (len(frames) + 1) * gap, cell_h + 2 * gap), (5, 6, 17, 255))
    for index, frame in enumerate(frames):
        filmstrip.alpha_composite(frame, (gap + index * (cell_w + gap), gap))
    filmstrip_path = output_dir / "filmstrip.png"
    filmstrip.convert("RGB").save(filmstrip_path)
    outputs.append(str(filmstrip_path.relative_to(repo_root)))
    return {"asset": asset["id"], "outputs": outputs}
