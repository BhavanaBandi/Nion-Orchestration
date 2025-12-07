import os
from pathlib import Path
from typing import List

from .vector_store import VectorStore

# Simple ingestion script that reads markdown files from the project root
# and populates the vector store. Adjust the paths as needed.

def ingest_project_docs(project_root: str = "c:/Users/Bhavana Bandi/Desktop/Nion Orchestration") -> VectorStore:
    """Ingest README and any .md files under the project root into a VectorStore.
    Returns the populated VectorStore instance.
    """
    store = VectorStore()
    docs: List[str] = []
    # Walk the directory and collect markdown files
    for root, _, files in os.walk(project_root):
        for f in files:
            if f.lower().endswith('.md'):
                file_path = os.path.join(root, f)
                try:
                    with open(file_path, 'r', encoding='utf-8') as fp:
                        content = fp.read()
                        docs.append(content)
                except Exception:
                    continue
    store.add_documents(docs)
    return store
