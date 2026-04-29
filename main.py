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
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_file_hash(file_path):
    """Calculates the SHA3-512 hash of a file."""
    sha3 = hashlib.sha3_512()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha3.update(chunk)
    return sha3.hexdigest()


def index_files(dirs, engine, processor, cache_base, force_reindex=False):
    """Indexes PDF files in the given directories."""
    for dir_path in dirs:
        p = Path(dir_path)
        if not p.exists():
            logger.warning(f"Stien {dir_path} findes ikke.")
            continue

        for pdf_file in p.glob("**/*.pdf"):
            try:
                file_hash = get_file_hash(pdf_file)
                # Normalize path for the database
                abs_path = str(pdf_file.absolute())

                if not force_reindex and engine.is_file_indexed(abs_path, file_hash):
                    logger.info(f"Springer over {pdf_file.name} (allerede indekseret).")
                    continue

                logger.info(f"Behandler {pdf_file.name}...")

                # Create a text cache for ripgrep
                relative_path = pdf_file.relative_to(p)
                txt_cache_path = cache_base / relative_path.with_suffix(".txt")
                txt_cache_path.parent.mkdir(parents=True, exist_ok=True)

                # Extract and store text for ripgrep
                subprocess.run(
                    ["pdftotext", str(pdf_file), str(txt_cache_path)], check=True
                )

                # Process for semantic search
                processor.process_pdf(str(pdf_file), engine)

                # Mark as indexed
                engine.mark_file_indexed(abs_path, file_hash)

            except Exception as e:
                logger.error(f"Fejl ved behandling af {pdf_file}: {e}")


def perform_search(query, engine, rg_searcher, cache_base):
    """Performs semantic and precise search and prints results."""
    logger.info(f"Søger efter: '{query}'")

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

    print("\n" + "=" * 50)
    print("--- Præcise resultater (ripgrep) ---")
    print("=" * 50)
    try:
        rg_results = rg_searcher.search(query, str(cache_base))
        if not rg_results:
            print("Ingen præcise resultater fundet.")
        for res in rg_results:
            print(f"Fil: {res['file']} (Linje {res['line']})")
            print(f"  {res['text']}")
            print("-" * 30)
    except Exception as e:
        logger.error(f"Fejl ved præcis søgning: {e}")


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
        # 2. Initialize engine
        engine = SearchEngine(db_path=db_path)
        processor = PDFProcessor()
        rg_searcher = RipgrepSearcher()

        # 3. Indexing
        index_files(
            args.dirs, engine, processor, cache_base, force_reindex=args.reindex
        )

        # 4. Search
        perform_search(args.query, engine, rg_searcher, cache_base)

    except KeyboardInterrupt:
        logger.info("\nAfbrudt af bruger.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Uventet fejl: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
