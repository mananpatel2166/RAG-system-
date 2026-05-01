import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
   
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model_name = model_name
        print(f"Loading embedding model: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        print("Embedding model ready.")

    def encode(self, texts: list[str] | str, batch_size: int = 64) -> np.ndarray:
        
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,   
            show_progress_bar=len(texts) > 100,
        )
        return embeddings.astype("float32")
