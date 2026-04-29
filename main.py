import argparse
import os
import sys
from pathlib import Path
from indsigten.core.search_engine import SearchEngine
from indsigten.core.pdf_processor import PDFProcessor
from indsigten.core.ripgrep_searcher import RipgrepSearcher

def main():
    parser = argparse.ArgumentParser(description="Indsigten CLI - Semantisk og præcis søgning i PDF'er")
    parser.add_argument("--dirs", nargs="+", help="Mapper der skal indekseres", required=True)
    parser.add_argument("query", help="Søgestreng")
    parser.add_argument("--db", default="indsigten.db", help="Sti til SQLite database")
    parser.add_argument("--cache-dir", default=".cache/indsigten", help="Sti til tekst-cache")
    
    args = parser.parse_args()
    
    # 1. Setup paths
    db_path = args.db
    cache_base = Path(os.path.expanduser("~")) / args.cache_dir
    cache_base.mkdir(parents=True, exist_ok=True)
    
    # 2. Initialize engine
    engine = SearchEngine(db_path=db_path)
    processor = PDFProcessor()
    rg_searcher = RipgrepSearcher()
    
    # 3. Indexing (if needed - for demo we always index)
    # In a real app we would check if already indexed
    print("Indekserer PDF-filer...")
    for dir_path in args.dirs:
        p = Path(dir_path)
        if not p.exists():
            print(f"Advarsel: Stien {dir_path} findes ikke.")
            continue
            
        for pdf_file in p.glob("**/*.pdf"):
            print(f"  Behandler {pdf_file.name}...")
            # Create a text cache for ripgrep
            relative_path = pdf_file.relative_to(p)
            txt_cache_path = cache_base / relative_path.with_suffix(".txt")
            txt_cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Extract and store text for ripgrep
            # (Note: PDFProcessor extracts page-by-page, for ripgrep we want full text or page-by-page)
            # For simplicity in this CLI, we let PDFProcessor add to SearchEngine 
            # and we manually run pdftotext for the cache
            import subprocess
            subprocess.run(["pdftotext", str(pdf_file), str(txt_cache_path)], check=True)
            
            processor.process_pdf(str(pdf_file), engine)

    # 4. Search
    print(f"\nSøger efter: '{args.query}'\n")
    
    print("--- Semantiske resultater ---")
    semantic_results = engine.search(args.query)
    for res in semantic_results:
        print(f"Score: {res['score']:.4f} | {res['doc_id']} (Side {res['page']})")
        print(f"  {res['text'][:100]}...")
        
    print("\n--- Præcise resultater (ripgrep) ---")
    rg_results = rg_searcher.search(args.query, str(cache_base))
    for res in rg_results:
        # Map back from cache filename to PDF filename if possible
        # For demo we just show the cache file
        print(f"Fil: {res['file']} (Linje {res['line']})")
        print(f"  {res['text']}")

if __name__ == "__main__":
    main()
