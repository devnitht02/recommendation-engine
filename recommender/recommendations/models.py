import json
import numpy as np
import pandas as pd
from django.db import models
# Create your models here.
from django.core.serializers.json import DjangoJSONEncoder
from hashlib import sha256

class NPArrayEncoder(DjangoJSONEncoder):
    """Custom JSON encoder for numpy arrays"""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
    
class WnTextEmbedding(models.Model):
    """
    Stores text embeddings with metadata for efficient retrieval
    """
    CONTENT_TYPE_CHOICES = [
        ('course', 'Course'),
        ('institution', 'Institution'),
        ('user', 'User Profile'),
    ]
    
    # Core fields
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        help_text="Type of content this embedding represents"
    )
    object_id = models.PositiveIntegerField(
        help_text="ID of the related object in its table"
    )
    
    # Text metadata
    text_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA256 hash of the original text for change detection"
    )
    original_text_length = models.PositiveIntegerField(
        help_text="Character length of original text"
    )
    
    # Embedding storage
    embedding = models.JSONField(
        encoder=NPArrayEncoder,
        help_text="Vector embedding stored as JSON array"
    )
    embedding_version = models.CharField(
        max_length=32,
        default="all-MiniLM-L6-v2",
        help_text="Model version used to generate embedding"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('content_type', 'object_id')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['text_hash']),
            models.Index(fields=['embedding_version']),
        ]
        verbose_name = "Text Embedding"
        verbose_name_plural = "Text Embeddings"
        db_table = 'wn_text_embedding'
    
    def __str__(self):
        return f"{self.content_type} #{self.object_id} ({self.embedding_version})"
    
    @classmethod
    def calculate_text_hash(cls, text: str) -> str:
        """Generate consistent hash for text"""
        return sha256(text.strip().encode('utf-8')).hexdigest()
    
    @classmethod
    def get_embedding(cls, content_type: str = None, object_id: int = None) -> pd.DataFrame:
        """Retrieve embedding from database"""
        try:
            filter_dict = {}
            if content_type:
                filter_dict["content_type"] = content_type

            if object_id:
                filter_dict["object_id"] = object_id

            record = cls.objects.filter(**filter_dict).values("content_type","object_id","embedding","embedding_version")
            return pd.DataFrame(list(record))
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def store_embedding(cls,content_type: str,object_id: int,text: str,embedding: np.ndarray,model_version: str = "all-MiniLM-L6-v2") -> "WnTextEmbedding":
        """Store or update an embedding"""
        text_hash = cls.calculate_text_hash(text)
        
        # Convert numpy array to list if needed
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        
        embedding_obj, created = cls.objects.update_or_create(
            content_type=content_type,
            object_id=object_id,
            defaults={
                'text_hash': text_hash,
                'original_text_length': len(text),
                'embedding': embedding,
                'embedding_version': model_version,
            }
        )
        
        return embedding_obj
    
    @classmethod
    def bulk_store_embeddings(cls,embeddings_data: list[dict],batch_size: int = 100) -> int:
        """
        Bulk store embeddings with format:
        [{
            'content_type': 'course',
            'object_id': 123,
            'text': "course description...",
            'embedding': np.array([...]),
            'model_version': 'all-MiniLM-L6-v2'
        }]
        """
        objs = []
        for data in embeddings_data:
            objs.append(cls(
                content_type=data['content_type'],
                object_id=data['object_id'],
                text_hash=cls.calculate_text_hash(data['text']),
                original_text_length=len(data['text']),
                embedding=data['embedding'],
                embedding_version=data.get('model_version', 'all-MiniLM-L6-v2')
            ))
        
        created_count = len(WnTextEmbedding.objects.bulk_create(
            objs,
            batch_size=batch_size,
            ignore_conflicts=True
        ))
        
        return created_count
    
    @property
    def embedding_vector(self) -> np.ndarray:
        """Get embedding as numpy array"""
        return np.array(self.embedding)