<<<<<<< HEAD
import hashlib
import io
=======
import io
import sys
>>>>>>> origin/main
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
<<<<<<< HEAD
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
=======
from unittest.mock import MagicMock

sys.modules.setdefault("hnswlib", MagicMock())
sys.modules.setdefault("sentence_transformers", MagicMock())
from main import get_page_from_cache_line, search_exact


class FakeSearcher:
    def __init__(self, results):
        self._results = results

    def search(self, query, search_dir):
        return self._results


class TestMain(unittest.TestCase):
    def test_get_page_from_cache_line(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "sample.txt"
            cache_file.write_text("side 1\ntekst\n\f\nside 2\n\f\nside 3\n", encoding="utf-8")

            self.assertEqual(get_page_from_cache_line(str(cache_file), 1), 1)
            self.assertEqual(get_page_from_cache_line(str(cache_file), 2), 1)
            self.assertEqual(get_page_from_cache_line(str(cache_file), 4), 2)
            self.assertEqual(get_page_from_cache_line(str(cache_file), 6), 3)

    def test_search_exact_reports_page_number(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "sample.txt"
            cache_file.write_text("side 1\ntekst\n\f\nmatch på side 2\n", encoding="utf-8")
            searcher = FakeSearcher(
                [{"file": str(cache_file), "line": 4, "text": "match på side 2"}]
            )

            output = io.StringIO()
            with redirect_stdout(output):
                search_exact("match", searcher, Path(tmpdir))

            self.assertIn("(Side 2)", output.getvalue())
            self.assertNotIn("(Linje 4)", output.getvalue())

    def test_search_exact_reports_unknown_page_when_cache_file_missing(self):
        searcher = FakeSearcher(
            [{"file": "/does/not/exist.txt", "line": 4, "text": "match"}]
        )

        output = io.StringIO()
        with redirect_stdout(output):
            search_exact("match", searcher, Path("/tmp"))

        self.assertIn("(Side ukendt)", output.getvalue())
>>>>>>> origin/main


if __name__ == "__main__":
    unittest.main()
