import argparse
import hashlib
import logging
import os
import subprocess
import sys
from pathlib import Path

from indsigten.core.pdf_processor import PDFProcessor
from indsigten.core.ripgrep_searcher import RipgrepSearcher
from indsigten.core.search_engine import SearchEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress verbose logging from external libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)


def get_file_hash(file_path):
    """Calculates the SHA2-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_pdf_files(dirs):
    """Gathers all PDF files from the given directories."""
    pdf_files = []
    for dir_path in dirs:
        p = Path(dir_path)
        if not p.exists():
            logger.warning(f"Stien {dir_path} findes ikke.")
            continue
        for f in p.glob("**/*.pdf"):
            pdf_files.append((f, p))
    return pdf_files


def sync_ripgrep_cache(pdf_files, engine, cache_base, force_reindex=False):
    """Phase 1: Ensure all PDF files have udtrukket text in the cache for ripgrep."""
    for pdf_file, _ in pdf_files:
        try:
            file_hash = get_file_hash(pdf_file)
            txt_cache_path = cache_base / f"{file_hash}.txt"
            
            if not force_reindex and txt_cache_path.exists():
                continue

            logger.info(f"Ekstraherer tekst til cache: {pdf_file.name}...")
            txt_cache_path.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["pdftotext", str(pdf_file), str(txt_cache_path)], check=True
            )
        except Exception as e:
            logger.error(f"Fejl ved ekstrahering af {pdf_file}: {e}")


def search_exact(query, rg_searcher, cache_base, hash_to_pdf_path=None):
    """Performs precise search and prints results."""
    print("\n" + "=" * 50)
    print("--- Præcise resultater (ripgrep) ---")
    print("=" * 50)
    try:
        rg_results = rg_searcher.search(query, str(cache_base))
        if not rg_results:
            print("Ingen præcise resultater fundet.")
        for res in rg_results:
<<<<<<< HEAD
            display_file = res["file"]
            if hash_to_pdf_path:
                hash_key = Path(res["file"]).stem
                display_file = hash_to_pdf_path.get(hash_key, display_file)

            print(f"Fil: {display_file} (Linje {res['line']})")
=======
            page = get_page_from_cache_line(res["file"], res["line"])
            page_text = str(page) if page is not None else "ukendt"
            print(f"Fil: {res['file']} (Side {page_text})")
>>>>>>> origin/main
            print(f"  {res['text']}")
            print("-" * 30)
    except Exception as e:
        logger.error(f"Fejl ved præcis søgning: {e}")


def get_page_from_cache_line(cache_file, line_number):
    """Converts a line number in a pdftotext cache file to a page number."""
    if line_number <= 1:
        return 1

    page = 1
    try:
        with open(cache_file, encoding="utf-8", errors="ignore") as file:
            for current_line_number, line in enumerate(file, start=1):
                if current_line_number >= line_number:
                    break
                page += line.count("\f")
        return page
    except OSError:
        return None


def index_semantically(pdf_files, engine, processor, force_reindex=False):
    """Phase 2: Perform semantic indexing (this will load the model)."""
    for pdf_file, _ in pdf_files:
        try:
            file_hash = get_file_hash(pdf_file)
            abs_path = str(pdf_file.absolute())

            if not force_reindex and engine.is_file_indexed(abs_path, file_hash):
                continue

            logger.info(f"Indekserer semantisk: {pdf_file.name}...")
            processor.process_pdf(str(pdf_file), engine)
            engine.mark_file_indexed(abs_path, file_hash)
        except Exception as e:
            logger.error(f"Fejl ved semantisk indeksering af {pdf_file}: {e}")


def search_semantic(query, engine):
    """Performs semantic search and prints results."""
    print("\n" + "=" * 50)
    print("--- Semantiske resultater ---")
    print("=" * 50)
    try:
        semantic_results = engine.search(query)
        if not semantic_results:
            print("Ingen semantiske resultater fundet.")
        for res in semantic_results:
            print(f"Score: {res['score']:.4f} | {res['doc_id']} (Side {res['page']})")
            print(f"  {res['text'][:150]}...")
            print("-" * 30)
    except Exception as e:
        logger.error(f"Fejl ved semantisk søgning: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Indsigten CLI - Semantisk og præcis søgning i PDF'er"
    )
    parser.add_argument(
        "--dirs", nargs="+", help="Mapper der skal indekseres", required=True
    )
    parser.add_argument("query", help="Søgestreng")
    parser.add_argument("--db", default="indsigten.db", help="Sti til SQLite database")
    parser.add_argument(
        "--cache-dir", default=".cache/indsigten", help="Sti til tekst-cache"
    )
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Gennemtving genindeksering af alle filer",
    )

    args = parser.parse_args()

    # 1. Setup paths
    db_path = args.db
    cache_base = Path(os.path.expanduser("~")) / args.cache_dir
    cache_base.mkdir(parents=True, exist_ok=True)

    try:
        # 2. Initialize components
        engine = SearchEngine(db_path=db_path)
        processor = PDFProcessor()
        rg_searcher = RipgrepSearcher()

        # 3. Gather files
        pdf_files = get_pdf_files(args.dirs)
        hash_to_pdf_path = {
            get_file_hash(pdf_file): str(pdf_file.absolute()) for pdf_file, _ in pdf_files
        }

        # 4. Phase 1 Indexing & Exact Search
        sync_ripgrep_cache(pdf_files, engine, cache_base, force_reindex=args.reindex)
        search_exact(args.query, rg_searcher, cache_base, hash_to_pdf_path=hash_to_pdf_path)

        # 5. Phase 2 Indexing & Semantic Search
        index_semantically(pdf_files, engine, processor, force_reindex=args.reindex)
        search_semantic(args.query, engine)

    except KeyboardInterrupt:
        logger.info("\nAfbrudt af bruger.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Uventet fejl: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
