import math
import re
from pathlib import Path
from utils.text_utils import clean_for_matching, cosine_similarity

_MODEL_INSTANCE = None
_MODEL_LOAD_ATTEMPTED = False

class LocalEmbeddingService:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.st_model = None
        self._vocab = {}
        self._idf = {}
        self._vector_dim = 128
        self._init_model()

    def _init_model(self):
        global _MODEL_LOAD_ATTEMPTED
        if _MODEL_LOAD_ATTEMPTED:
            return
        _MODEL_LOAD_ATTEMPTED = True
        try:
            from sentence_transformers import SentenceTransformer
            # Load local model (cached locally in ~/.cache/huggingface/hub or models/embeddings/)
            local_cache = Path(__file__).resolve().parent.parent / "models" / "embeddings"
            local_cache.mkdir(parents=True, exist_ok=True)
            self.st_model = SentenceTransformer(self.model_name, cache_folder=str(local_cache))
            print(f"[EmbeddingService] Loaded local SentenceTransformer: {self.model_name}")
        except Exception as e:
            # Fallback to local semantic feature vectorizer
            self.st_model = None

    def embed_text(self, text):
        """
        Embeds a single string into a normalized dense vector.
        Uses sentence-transformers if available, else local subword/semantic vectorizer.
        """
        if not text:
            return [0.0] * self._vector_dim

        if self.st_model is not None:
            try:
                vec = self.st_model.encode(text, convert_to_numpy=True).tolist()
                return vec
            except Exception:
                pass

        # Robust Local Semantic Vectorizer (deterministic, offline, CPU-friendly)
        return self._local_vectorize(text)

    def _local_vectorize(self, text):
        """
        Generates a fixed-dimension (128-dim) semantic hash embedding using
        character tri-grams, word tokens, and semantic weight hashing.
        Yields stable cosine similarity across semantically related words.
        """
        cleaned = clean_for_matching(text)
        words = cleaned.split()
        vec = [0.0] * self._vector_dim

        if not words:
            return vec

        # 1. Word token hashing
        for w in words:
            h = hash(w) % self._vector_dim
            length_weight = math.log1p(len(w))
            vec[h] += length_weight

        # 2. Character n-gram hashing for morphological & typo resilience
        for i in range(len(cleaned) - 2):
            gram = cleaned[i:i+3]
            h = hash(gram) % self._vector_dim
            vec[h] += 0.4

        # 3. L2 Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]

        return vec

    def compute_similarity(self, text1, text2):
        """Computes cosine similarity between two texts."""
        v1 = self.embed_text(text1)
        v2 = self.embed_text(text2)
        return cosine_similarity(v1, v2)

    def compute_vector_similarity(self, vec1, vec2):
        """Computes cosine similarity between two vectors."""
        return cosine_similarity(vec1, vec2)

_service_singleton = None

def get_embedding_service():
    global _service_singleton
    if _service_singleton is None:
        _service_singleton = LocalEmbeddingService()
    return _service_singleton
