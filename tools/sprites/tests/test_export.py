from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(TOOLS))
from common import SpriteError, export_asset, run  # noqa: E402


def make_asset() -> dict:
    return {
        "id": "test-asset",
        "source": "source.aseprite",
        "preview_scale": 1,
        "animation_tags": ["idle"],
        "exports": {
            "png": "asset.png",
            "gif": "asset.gif",
            "sheet": "sheet.png",
            "atlas": "sheet.json",
        },
    }


def fake_aseprite(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    if "--save-as" in command:
        Path(command[-1]).write_text("new", encoding="utf-8")
    if "--sheet" in command:
        Path(command[command.index("--sheet") + 1]).write_text("new", encoding="utf-8")
        Path(command[command.index("--data") + 1]).write_text("{}", encoding="utf-8")
    return subprocess.CompletedProcess(command, 0, stdout="", stderr="")


class ExportSafetyTests(unittest.TestCase):
    def test_run_times_out_with_controlled_error(self):
        with patch("common.subprocess.run", side_effect=subprocess.TimeoutExpired(["aseprite"], 1)):
            with self.assertRaisesRegex(SpriteError, "timed out"):
                run(["aseprite"])

    def test_export_uses_system_temporary_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            repo_root = Path(temp)
            asset = make_asset()
            with (
                patch("common.tempfile.TemporaryDirectory", wraps=tempfile.TemporaryDirectory) as temporary,
                patch("common.run", side_effect=fake_aseprite),
            ):
                export_asset(repo_root, asset)
            self.assertNotIn("dir", temporary.call_args.kwargs)

    def test_export_rolls_back_replaced_targets_on_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            repo_root = Path(temp)
            asset = make_asset()
            for relative in asset["exports"].values():
                path = repo_root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("old", encoding="utf-8")

            real_replace = os.replace
            calls = 0

            def fail_second_replace(source, target):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("replace failed")
                return real_replace(source, target)

            with (
                patch("common.run", side_effect=fake_aseprite),
                patch("os.replace", side_effect=fail_second_replace),
            ):
                with self.assertRaisesRegex(SpriteError, "replace failed"):
                    export_asset(repo_root, asset)

            for relative in asset["exports"].values():
                self.assertEqual((repo_root / relative).read_text(encoding="utf-8"), "old")
    def test_export_removes_new_target_when_replacement_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            repo_root = Path(temp)
            asset = make_asset()
            real_replace = os.replace
            calls = 0

            def fail_second_replace(source, target):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("replace failed")
                return real_replace(source, target)

            with (
                patch("common.run", side_effect=fake_aseprite),
                patch("os.replace", side_effect=fail_second_replace),
            ):
                with self.assertRaisesRegex(SpriteError, "replace failed"):
                    export_asset(repo_root, asset)

            for relative in asset["exports"].values():
                self.assertFalse((repo_root / relative).exists())


if __name__ == "__main__":
    unittest.main()
