from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(TOOLS))
from common import (  # noqa: E402
    SpriteError,
    contact_sheet,
    load_manifest,
    validate_atlas_data,
    write_proof,
)


def valid_asset(asset_id: str = "a") -> dict:
    return {
        "id": asset_id,
        "status": "prototype",
        "source": "source.aseprite",
        "spec": "SPEC.md",
        "palette": "palette.gpl",
        "max_colors": 8,
        "preview_scale": 1,
        "native": {"width": 2, "height": 2},
        "required_layers": ["Sprite"],
        "animation_tags": ["idle"],
        "exports": {"png": "asset.png", "gif": "asset.gif", "sheet": "sheet.png", "atlas": "sheet.json"},
    }


class ValidationSafetyTests(unittest.TestCase):
    def test_manifest_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(SpriteError, "Invalid manifest JSON"):
                load_manifest(path)

    def test_manifest_rejects_malformed_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            for data in ({"schema_version": 1, "assets": ["not-an-object"]}, {"schema_version": 1, "assets": [{"id": "a", "status": "prototype"}]}):
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.subTest(data=data):
                    with self.assertRaisesRegex(SpriteError, "Manifest asset"):
                        load_manifest(path)

    def test_manifest_rejects_invalid_asset_shapes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            invalid_assets = []
            asset = valid_asset()
            asset["exports"]["png"] = None
            invalid_assets.append(asset)
            asset = valid_asset()
            asset["animation_tags"] = []
            invalid_assets.append(asset)
            asset = valid_asset()
            asset["native"]["width"] = 0
            invalid_assets.append(asset)
            for asset in invalid_assets:
                path.write_text(json.dumps({"schema_version": 1, "assets": [asset]}), encoding="utf-8")
                with self.subTest(asset=asset):
                    with self.assertRaisesRegex(SpriteError, "Manifest asset"):
                        load_manifest(path)

    def test_write_proof_records_missing_files(self):
        with tempfile.TemporaryDirectory() as temp:
            repo_root = Path(temp)
            asset = valid_asset()
            finding = {"severity": "error", "code": "missing_file", "message": "Missing source"}
            proof_path = write_proof(repo_root, asset, [finding])
            proof = json.loads(proof_path.read_text(encoding="utf-8"))
            self.assertEqual(proof["result"], "fail")
            self.assertIsNone(proof["files"][asset["source"]])

    def test_contact_sheet_rejects_empty_atlas(self):
        with tempfile.TemporaryDirectory() as temp:
            repo_root = Path(temp)
            asset = valid_asset()
            sheet = repo_root / asset["exports"]["sheet"]
            sheet.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2)).save(sheet)
            (repo_root / asset["exports"]["atlas"]).write_text(json.dumps({"frames": []}), encoding="utf-8")
            with self.assertRaisesRegex(SpriteError, "no frames"):
                contact_sheet(repo_root, asset)

    def test_contact_sheet_rejects_malformed_frame_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            repo_root = Path(temp)
            asset = valid_asset()
            sheet = repo_root / asset["exports"]["sheet"]
            sheet.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2)).save(sheet)
            malformed_frames = [
                ["not-an-object"],
                [{"frame": {"x": 0, "y": 0}}],
                [{"frame": {"x": 0, "y": 0, "w": "2", "h": 2}}],
            ]
            for frames in malformed_frames:
                (repo_root / asset["exports"]["atlas"]).write_text(json.dumps({"frames": frames}), encoding="utf-8")
                with self.subTest(frames=frames):
                    with self.assertRaisesRegex(SpriteError, "Invalid atlas frame"):
                        contact_sheet(repo_root, asset)

    def test_atlas_rejects_non_positive_durations(self):
        atlas = {
            "meta": {"size": {"w": 2, "h": 2}, "frameTags": [{"name": "idle"}]},
            "frames": [{"duration": 0}, {"duration": 100}],
        }
        errors = validate_atlas_data(atlas, {"width": 2, "height": 2}, {"width": 2, "height": 2}, ["idle"])
        self.assertTrue(any("positive" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
