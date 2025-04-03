# recommendations/services/embedding_service.py
from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    _model = None
    
    @classmethod
    def get_model(cls):
        if cls._model is None:
            try:
                cls._model = SentenceTransformer(
                    "sentence-transformers/all-MiniLM-L6-v2",
                )
                logger.info("Successfully loaded SentenceTransformer model")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}")
                raise
        return cls._model
    
    @classmethod
    def generate_embeddings(cls, texts: list) -> np.ndarray:
        """Generate embeddings for a list of text strings"""
        model = cls.get_model()
        return model.encode(texts)