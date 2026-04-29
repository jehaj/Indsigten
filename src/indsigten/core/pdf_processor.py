import subprocess
import re

class PDFProcessor:
    def get_page_count(self, pdf_path):
        result = subprocess.run(
            ["pdfinfo", pdf_path],
            capture_output=True,
            text=True,
            check=True
        )
        match = re.search(r"Pages:\s+(\d+)", result.stdout)
        if match:
            return int(match.group(1))
        return 0

    def extract_page_text(self, pdf_path, page):
        result = subprocess.run(
            ["pdftotext", "-f", str(page), "-l", str(page), pdf_path, "-"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    def process_pdf(self, pdf_path, search_engine):
        page_count = self.get_page_count(pdf_path)
        for page in range(1, page_count + 1):
            text = self.extract_page_text(pdf_path, page)
            if text.strip():
                search_engine.add_page(pdf_path, page, text)
