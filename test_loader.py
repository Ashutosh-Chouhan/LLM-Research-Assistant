"""
Quick sanity check for the loader + splitter.

    python test_loader.py
"""

from src.loader import load_pdf
from src.splitter import split_documents

documents = load_pdf("data/research_paper.pdf")

print("Total pages:", len(documents))
print("\nFirst page metadata:\n", documents[0].metadata)
print("\nFirst 500 chars of page 1:\n", documents[0].page_content[:500])

chunks = split_documents(documents)
print("\nTotal chunks:", len(chunks))
print("\nFirst chunk:\n", chunks[0].page_content[:300])
