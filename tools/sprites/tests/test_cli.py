from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import contact_sheet  # noqa: E402
import export  # noqa: E402
import verify  # noqa: E402
from common import SpriteError  # noqa: E402


class CliFailureTests(unittest.TestCase):
    def test_export_cli_reports_sprite_error(self):
        with (
            patch.object(export, "get_asset", side_effect=SpriteError("boom")),
            patch.object(sys, "argv", ["export.py", "test-asset"]),
            redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(export.main(), 2)

    def test_contact_sheet_cli_reports_sprite_error(self):
        with (
            patch.object(contact_sheet, "get_asset", side_effect=SpriteError("boom")),
            patch.object(sys, "argv", ["contact_sheet.py", "test-asset"]),
            redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(contact_sheet.main(), 2)

    def test_verify_cli_reports_sprite_error(self):
        with (
            patch.object(verify, "load_manifest", side_effect=SpriteError("boom")),
            patch.object(sys, "argv", ["verify.py", "--all"]),
            redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(verify.main(), 2)


if __name__ == "__main__":
    unittest.main()
