from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_saved_lists.cli import main
from google_saved_lists.scraper import BrowserArtifacts


class CliTests(unittest.TestCase):
    def test_debug_output_dir_writes_dump_and_stdout_payload(self) -> None:
        artifacts = BrowserArtifacts(
            runtime_state=["runtime"],
            script_texts=["script"],
            html="<html></html>",
        )
        parsed_payload = {
            "source_url": "https://example.com/list",
            "list_id": "list-id",
            "title": "List",
            "description": None,
            "places": [],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            stdout = io.StringIO()
            with (
                patch("google_saved_lists.cli.collect_browser_artifacts", return_value=artifacts),
                patch("google_saved_lists.cli.write_debug_dump") as write_debug_dump,
                patch("google_saved_lists.cli.parse_saved_list_artifacts") as parse_saved_list,
                patch(
                    "sys.argv",
                    [
                        "google-saved-lists",
                        "https://example.com/list",
                        "--debug-output-dir",
                        tmp_dir,
                    ],
                ),
                redirect_stdout(stdout),
            ):
                parse_saved_list.return_value.to_dict.return_value = parsed_payload

                exit_code = main()

            self.assertEqual(exit_code, 0)
            write_debug_dump.assert_called_once_with(
                "https://example.com/list",
                runtime_state=["runtime"],
                script_texts=["script"],
                html="<html></html>",
                output_dir=Path(tmp_dir),
            )
            self.assertEqual(json.loads(stdout.getvalue()), parsed_payload)

    def test_dump_debug_output_uses_default_hidden_directory(self) -> None:
        artifacts = BrowserArtifacts(
            runtime_state=["runtime"],
            script_texts=["script"],
            html="<html></html>",
        )
        parsed_payload = {
            "source_url": "https://example.com/list",
            "list_id": "list-id",
            "title": "List",
            "description": None,
            "places": [],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            stdout = io.StringIO()
            with (
                patch("google_saved_lists.cli.collect_browser_artifacts", return_value=artifacts),
                patch("google_saved_lists.cli.write_debug_dump") as write_debug_dump,
                patch("google_saved_lists.cli.parse_saved_list_artifacts") as parse_saved_list,
                patch("google_saved_lists.cli.os.getcwd", return_value=tmp_dir),
                patch(
                    "sys.argv",
                    [
                        "google-saved-lists",
                        "https://example.com/list",
                        "--dump-debug-output",
                    ],
                ),
                redirect_stdout(stdout),
            ):
                parse_saved_list.return_value.to_dict.return_value = parsed_payload

                exit_code = main()

            self.assertEqual(exit_code, 0)
            write_debug_dump.assert_called_once_with(
                "https://example.com/list",
                runtime_state=["runtime"],
                script_texts=["script"],
                html="<html></html>",
                output_dir=Path(tmp_dir) / ".google-saved-lists-debug",
            )
            self.assertEqual(json.loads(stdout.getvalue()), parsed_payload)

    def test_debug_output_dir_overrides_default_dump_directory(self) -> None:
        artifacts = BrowserArtifacts(
            runtime_state=["runtime"],
            script_texts=["script"],
            html="<html></html>",
        )
        parsed_payload = {
            "source_url": "https://example.com/list",
            "list_id": "list-id",
            "title": "List",
            "description": None,
            "places": [],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            stdout = io.StringIO()
            explicit_dir = Path(tmp_dir) / "custom-debug"
            with (
                patch("google_saved_lists.cli.collect_browser_artifacts", return_value=artifacts),
                patch("google_saved_lists.cli.write_debug_dump") as write_debug_dump,
                patch("google_saved_lists.cli.parse_saved_list_artifacts") as parse_saved_list,
                patch("google_saved_lists.cli.os.getcwd", return_value=tmp_dir),
                patch(
                    "sys.argv",
                    [
                        "google-saved-lists",
                        "https://example.com/list",
                        "--dump-debug-output",
                        "--debug-output-dir",
                        str(explicit_dir),
                    ],
                ),
                redirect_stdout(stdout),
            ):
                parse_saved_list.return_value.to_dict.return_value = parsed_payload

                exit_code = main()

            self.assertEqual(exit_code, 0)
            write_debug_dump.assert_called_once_with(
                "https://example.com/list",
                runtime_state=["runtime"],
                script_texts=["script"],
                html="<html></html>",
                output_dir=explicit_dir,
            )
            self.assertEqual(json.loads(stdout.getvalue()), parsed_payload)
