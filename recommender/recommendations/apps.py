import logging
from django.apps import AppConfig
from django.core.cache import cache
from django.conf import settings
from .services.embedding_service import EmbeddingService
from .services.search_utils import search_engine

logger = logging.getLogger(__name__)

class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'

    def ready(self):
        """Preload embeddings into cache when the Django app starts."""
        CACHE_KEY = "institution_embeddings"
        if not cache.get(CACHE_KEY):  # Check if cache is empty
            from .models import WnTextEmbedding
            print("Preloading embeddings into cache...")
            df = WnTextEmbedding.get_embedding()
            cache.set(CACHE_KEY, df, timeout=60 * 60)  # Cache for 1 hour
        else:
            print("Embeddings already cached.")

        """Pre-load embedding model when app starts"""
        try:
            EmbeddingService.get_model()
        except Exception as e:
            logger.warning(f"Couldn't pre-load embedding model: {str(e)}")

        search_engine.initialize()