import json
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        # This downloads the model once, then uses it locally
        self.model = SentenceTransformer(model_name)

    def encode_text(self, text: str) -> np.ndarray:
        if not text:
            text = ""
        emb = self.model.encode([text], normalize_embeddings=True)
        return emb[0].astype("float32")

    @staticmethod
    def embedding_to_json(vec: np.ndarray) -> str:
        return json.dumps(vec.tolist())

    @staticmethod
    def embedding_from_json(data: str | None) -> np.ndarray | None:
        if not data:
            return None
        arr = np.array(json.loads(data), dtype="float32")
        return arr
