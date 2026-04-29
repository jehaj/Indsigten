import unittest
from unittest.mock import MagicMock, patch, call
import subprocess

class TestPDFProcessor(unittest.TestCase):
    @patch('subprocess.run')
    def test_get_page_count(self, mock_run):
        from indsigten.core.pdf_processor import PDFProcessor
        
        # Mock pdfinfo output
        mock_run.return_value.stdout = "Pages:          10\n"
        mock_run.return_value.returncode = 0
        
        processor = PDFProcessor()
        count = processor.get_page_count("dummy.pdf")
        
        self.assertEqual(count, 10)
        mock_run.assert_called_with(["pdfinfo", "dummy.pdf"], capture_output=True, text=True, check=True)

    @patch('subprocess.run')
    def test_extract_page_text(self, mock_run):
        from indsigten.core.pdf_processor import PDFProcessor
        
        # Mock pdftotext output
        mock_run.return_value.stdout = "Extracted text content"
        mock_run.return_value.returncode = 0
        
        processor = PDFProcessor()
        text = processor.extract_page_text("dummy.pdf", page=1)
        
        self.assertEqual(text, "Extracted text content")
        mock_run.assert_called_with(
            ["pdftotext", "-f", "1", "-l", "1", "dummy.pdf", "-"],
            capture_output=True, text=True, check=True
        )

    @patch('indsigten.core.pdf_processor.PDFProcessor.get_page_count')
    @patch('indsigten.core.pdf_processor.PDFProcessor.extract_page_text')
    def test_process_pdf(self, mock_extract, mock_get_count):
        from indsigten.core.pdf_processor import PDFProcessor
        
        mock_get_count.return_value = 2
        mock_extract.side_effect = ["Page 1 text", "Page 2 text"]
        
        mock_engine = MagicMock()
        
        processor = PDFProcessor()
        processor.process_pdf("dummy.pdf", mock_engine)
        
        self.assertEqual(mock_engine.add_page.call_count, 2)
        mock_engine.add_page.assert_has_calls([
            call("dummy.pdf", 1, "Page 1 text"),
            call("dummy.pdf", 2, "Page 2 text")
        ])

if __name__ == '__main__':
    unittest.main()
