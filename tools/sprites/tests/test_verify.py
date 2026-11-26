from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import verify  # noqa: E402


class VerifyProofTests(unittest.TestCase):
    def test_failed_verification_replaces_prior_passing_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            repo_root = Path(temp)
            asset = {
                "id": "test-asset",
                "status": "prototype",
                "source": "source.aseprite",
                "spec": "SPEC.md",
                "palette": "palette.gpl",
                "exports": {"png": "asset.png"},
            }
            files = [asset["source"], asset["spec"], asset["palette"], *asset["exports"].values()]
            for relative in files:
                path = repo_root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(relative, encoding="utf-8")

            proof_path = repo_root / "sprites" / "proofs" / "test-asset.json"
            proof_path.parent.mkdir(parents=True)
            proof_path.write_text(json.dumps({"result": "pass"}) + "\n", encoding="utf-8")
            finding = {"severity": "ERROR", "code": "test_failure", "message": "Failed verification"}

            with (
                patch.object(verify, "REPO_ROOT", repo_root),
                patch.object(verify, "load_manifest", return_value={"assets": [asset]}),
                patch.object(verify, "validate_asset", return_value=[finding]),
                patch.object(sys, "argv", ["verify.py", "test-asset"]),
                redirect_stdout(io.StringIO()),
            ):
                exit_code = verify.main()

            proof = json.loads(proof_path.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 1)
            self.assertEqual(proof["result"], "fail")
            self.assertEqual(proof["findings"], [finding])


if __name__ == "__main__":
    unittest.main()
