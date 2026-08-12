"""
Ingestion script -- ise ek baar chalao, index ban jayega.

    python ingest.py                # data/ folder ke saare PDFs
    python ingest.py data/paper.pdf # sirf ek PDF

Kya hota hai:
    PDF  ->  pages  ->  chunks  ->  embeddings  ->  vector_db/ me save
"""

import sys

from src.config import DATA_DIR, VECTOR_DB_DIR
from src.loader import load_pdf, load_pdfs_from_dir
from src.splitter import split_documents
from src.vectorstore import build_vectorstore


def main() -> None:
    # Step 1: PDF load karo
    if len(sys.argv) > 1:
        target = sys.argv[1]
        print(f"[1/4] Loading PDF: {target}")
        documents = load_pdf(target)
    else:
        print(f"[1/4] Loading all PDFs from: {DATA_DIR}")
        documents = load_pdfs_from_dir(DATA_DIR)

    print(f"      -> {len(documents)} pages loaded")

    # Step 2: chunks banao
    print("[2/4] Splitting into chunks...")
    chunks = split_documents(documents)
    print(f"      -> {len(chunks)} chunks banaye")

    # Step 3: embeddings + save
    print("[3/4] Creating embeddings and building index (thoda time lagega)...")
    build_vectorstore(chunks, reset=True)

    print(f"[4/4] Done. Index saved at: {VECTOR_DB_DIR}")
    print("\nAb app chalao:  streamlit run app.py")


if __name__ == "__main__":
    main()
