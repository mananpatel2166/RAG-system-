import numpy as np
import faiss

from app.embedder import Embedder


class Retriever:

    def __init__(self, chunks: list[str], index: faiss.IndexFlatIP) -> None:
        self.chunks = chunks
        self.index  = index

   
    @classmethod
    def from_chunks(cls, chunks: list[str], embedder: Embedder) -> "Retriever":
        """
        Embed *chunks* and build a FAISS index.

        Args:
            chunks:   Non-empty text chunks from the PDF.
            embedder: Shared Embedder instance.

        Returns:
            A ready-to-query Retriever.
        """
        vectors = embedder.encode(chunks)         
        dim     = vectors.shape[1]

        index = faiss.IndexFlatIP(dim)     
        index.add(vectors)

        return cls(chunks=chunks, index=index)

    def retrieve(self, query: str, embedder: Embedder, k: int = 4) -> list[str]:
        
        k = min(k, self.index.ntotal)
        if k == 0:
            return []

        q_vec     = embedder.encode(query)         
        scores, idxs = self.index.search(q_vec, k) 

        return [self.chunks[i] for i in idxs[0] if i >= 0]
