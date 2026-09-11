import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
