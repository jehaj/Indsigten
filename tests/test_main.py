import hashlib
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

import main


class TestMainCacheFlow(unittest.TestCase):
    def test_get_file_hash_uses_sha256(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "sample.pdf"
            file_path.write_bytes(b"indsigten")

            expected_hash = hashlib.sha256(b"indsigten").hexdigest()
            self.assertEqual(main.get_file_hash(file_path), expected_hash)

    @patch("main.subprocess.run")
    @patch("main.get_file_hash", return_value="abc123")
    def test_sync_ripgrep_cache_reuses_hash_cache(self, _mock_hash, mock_subprocess_run):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            parent_dir = tmp_path / "Natural Language Processing (NLP)"
            slides_dir = parent_dir / "Slides"
            slides_dir.mkdir(parents=True)

            pdf_file = slides_dir / "lesson.pdf"
            pdf_file.write_bytes(b"%PDF-1.4")

            cache_base = tmp_path / "cache"
            cache_base.mkdir(parents=True)
            (cache_base / "abc123.txt").write_text("cached")

            pdf_files = [(pdf_file, parent_dir), (pdf_file, slides_dir)]
            main.sync_ripgrep_cache(pdf_files, MagicMock(), cache_base)

            mock_subprocess_run.assert_not_called()

    def test_search_exact_prints_pdf_path_for_hash_cache_entries(self):
        rg_searcher = MagicMock()
        rg_searcher.search.return_value = [
            {"file": "/tmp/cache/abc123.txt", "line": 7, "text": "match text"}
        ]

        out = io.StringIO()
        with redirect_stdout(out):
            main.search_exact(
                "match",
                rg_searcher,
                Path("/tmp/cache"),
                hash_to_pdf_path={"abc123": "/docs/Slides/lesson.pdf"},
            )

        output = out.getvalue()
        self.assertIn("Fil: /docs/Slides/lesson.pdf (Linje 7)", output)
        self.assertNotIn("abc123.txt", output)


if __name__ == "__main__":
    unittest.main()
