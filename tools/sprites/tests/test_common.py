from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from common import load_manifest, parse_gpl, validate_atlas_data, validate_export_pixels  # noqa: E402


class GplTests(unittest.TestCase):
    def test_parse_gpl_counts_unique_colours(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "palette.gpl"
            path.write_text("GIMP Palette\nName: Test\nColumns: 2\n#\n255 0 0 Red\n  0 255 0 Green\n", encoding="utf-8")
            self.assertEqual(parse_gpl(path), ["#ff0000", "#00ff00"])

    def test_parse_gpl_rejects_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "palette.gpl"
            path.write_text("GIMP Palette\n#\n255 0 0 Red\n255 0 0 Again\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "duplicate"):
                parse_gpl(path)


class ManifestTests(unittest.TestCase):
    def test_duplicate_asset_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            path.write_text(json.dumps({"schema_version": 1, "assets": [{"id": "a", "status": "prototype"}, {"id": "a", "status": "review"}]}), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "duplicate"):
                load_manifest(path)


class AtlasTests(unittest.TestCase):
    def test_valid_atlas_passes(self):
        atlas = {
            "meta": {"size": {"w": 10, "h": 10}, "frameTags": [{"name": "idle"}]},
            "frames": [{"duration": 100}, {"duration": 160}],
        }
        self.assertEqual(validate_atlas_data(atlas, {"width": 10, "height": 10}, {"width": 4, "height": 4}, ["idle"]), [])

    def test_uniform_timing_and_missing_tag_fail(self):
        atlas = {
            "meta": {"size": {"w": 10, "height": 10}, "frameTags": []},
            "frames": [{"duration": 100}, {"duration": 100}],
        }
        errors = validate_atlas_data(atlas, {"width": 10, "height": 10}, {"width": 4, "height": 4}, ["idle"])
        self.assertTrue(any("uniform" in error for error in errors))
        self.assertTrue(any("Missing animation tags" in error for error in errors))


class PixelTests(unittest.TestCase):
    def test_partial_alpha_and_off_palette_are_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "pixel.png"
            image = Image.new("RGBA", (2, 1))
            image.putpixel((0, 0), (255, 0, 0, 128))
            image.putpixel((1, 0), (0, 0, 255, 255))
            image.save(path)
            errors = validate_export_pixels(path, {"#ff0000"})
            self.assertTrue(any("Partial alpha" in error for error in errors))
            self.assertTrue(any("Off-palette" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
