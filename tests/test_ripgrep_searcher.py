import unittest
from unittest.mock import MagicMock, patch
import subprocess

class TestRipgrepSearcher(unittest.TestCase):
    @patch('subprocess.run')
    def test_search(self, mock_run):
        from indsigten.core.ripgrep_searcher import RipgrepSearcher
        
        # Mock ripgrep output
        # Format: file:line:content
        mock_run.return_value.stdout = "demo/test.txt:1:Some matching text\ndemo/test.txt:5:Another match\n"
        mock_run.return_value.returncode = 0
        
        searcher = RipgrepSearcher()
        results = searcher.search("matching", search_dir="demo")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['file'], "demo/test.txt")
        self.assertEqual(results[0]['line'], 1)
        self.assertEqual(results[0]['text'], "Some matching text")
        
        mock_run.assert_called_with(
            ["rg", "--line-number", "--with-filename", "--no-heading", "matching", "demo"],
            capture_output=True, text=True, check=False
        )

if __name__ == '__main__':
    unittest.main()
