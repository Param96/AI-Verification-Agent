from sentence_transformers import SentenceTransformer, util
from config import EMBEDDING_MODEL_NAME
from utils.logger import logger


class EmbeddingEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info(f"Loading Embedding Model: {EMBEDDING_MODEL_NAME}")
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Embedding Model loaded successfully.")

    def get_embedding(self, text: str):
        if not text:
            return None
        return self.model.encode(str(text), convert_to_tensor=True)

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Returns cosine similarity between two texts [0, 1]."""
        if not text1 or not text2:
            return 0.0

        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        cosine_score = util.cos_sim(emb1, emb2).item()
        return max(0.0, cosine_score)  # Return bound to 0-1
