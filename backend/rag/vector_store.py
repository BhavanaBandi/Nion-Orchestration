import os
from pathlib import Path
from typing import List
import faiss
from sentence_transformers import SentenceTransformer

class VectorStore:
    """Simple FAISS vector store for text documents.
    Stores embeddings and original texts in parallel lists.
    """
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(embedding_model)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.texts: List[str] = []

    def add_documents(self, docs: List[str]):
        """Add a list of documents to the store.
        Each document is embedded and added to the FAISS index.
        """
        if not docs:
            return
        embeddings = self.model.encode(docs, convert_to_numpy=True)
        self.index.add(embeddings)
        self.texts.extend(docs)

    def query(self, question: str, top_k: int = 3) -> List[str]:
        """Return the top_k most similar document texts for the question."""
        if self.index.ntotal == 0:
            return []
        q_vec = self.model.encode([question], convert_to_numpy=True)
        distances, indices = self.index.search(q_vec, top_k)
        results = []
        for idx in indices[0]:
            if idx < len(self.texts):
                results.append(self.texts[idx])
        return results
