import numpy as np
from recommendations.models import WnTextEmbedding
from sklearn.metrics.pairwise import cosine_similarity
from .embedding_service import EmbeddingService
from institutions.models import WnInstitution, WnCourse
from django.db.models import Case, When, Value, IntegerField
from django.core.cache import cache
import numpy as np

CACHE_KEY = "institution_embeddings"
CACHE_TIMEOUT = 60 * 60  # Cache for 1 hour

# Try to fetch embeddings from cache
df = cache.get(CACHE_KEY)


class RecommendationService:

    def global_search(self, query: str, top_n: int = 50) -> list:
        """
        Returns mixed results sorted by similarity
        Args:
            query: Search query
            top_n: Total number of results to return
        Returns:
            [
                {
                    "type": "institution",
                    "id": 123,
                    "name": "MIT",
                    "similarity": 0.91,
                    "metadata": {...}
                },
                {
                    "type": "course", 
                    "id": 456,
                    "name": "Computer Science",
                    "similarity": 0.90,
                    "metadata": {...}
                }
            ]
        """
        # 1. Get all embeddings and calculate similarities
        df = cache.get(CACHE_KEY)

        if df is None:
            print("Cache miss! Fetching from DB...")
            df = WnTextEmbedding.get_embedding()
            cache.set(CACHE_KEY, df, CACHE_TIMEOUT) 
            
        query_embedding = EmbeddingService.get_model().encode([query])[0]

        df["similarity"] = df["embedding"].apply(
            lambda x: self._cosine_similarity(np.array(x), query_embedding)
        )
        priority = self._detect_priority(query)
        if priority == 'institution':
            df.loc[df['content_type'] == 'institution', 'similarity'] *= 1.2  # 20% boost
        elif priority == 'course':
            df.loc[df['content_type'] == 'course', 'similarity'] *= 1.2

        # 2. Get top results across both types
        combined_results = df.sort_values('similarity', ascending=False).head(top_n * 2)

        # 3. Separate IDs by type
        course_ids = combined_results[combined_results['content_type'] == 'course']['object_id'].tolist()
        institution_ids = combined_results[combined_results['content_type'] == 'institution']['object_id'].tolist()

        # 4. Fetch all objects in single queries
        courses = WnCourse.objects.filter(pk__in=course_ids)
        institutions = WnInstitution.objects.filter(pk__in=institution_ids)

        # 5. Create mapping for quick lookup
        course_map = {c.pk: c for c in courses}
        institution_map = {i.pk: i for i in institutions}

        # 6. Build unified results list
        final_results = []
        for _, row in combined_results.iterrows():
            if row['content_type'] == 'course' and row['object_id'] in course_map:
                course = course_map[row['object_id']]
                final_results.append({
                    'type': 'course',
                    'id': course.pk,
                    'name': course.course_name,
                    'similarity': round(row['similarity'], 4),
                })
            elif row['content_type'] == 'institution' and row['object_id'] in institution_map:
                institution = institution_map[row['object_id']]
                final_results.append({
                    'type': 'institution',
                    'id': institution.pk,
                    'name': institution.institution_name,
                    'similarity': round(row['similarity'], 4),
                })
        return final_results[:top_n]

    def _detect_priority(self, query: str) -> str:
        """
        Detect content type priority based on keywords
        Returns: 'institution', 'course', or None
        """
        query_lower = query.lower()

        institution_keywords = [
            'university', 'college', 'institute',
            'institution', 'school', 'academy'
        ]

        course_keywords = [
            'course', 'class', 'lecture', 'program',
            'subject', 'module', 'curriculum'
        ]

        institution_matches = sum(
            keyword in query_lower for keyword in institution_keywords
        )
        course_matches = sum(
            keyword in query_lower for keyword in course_keywords
        )

        if institution_matches > course_matches:
            return 'institution'
        elif course_matches > institution_matches:
            return 'course'
        return None

    @staticmethod
    def _cosine_similarity(vec_a, vec_b):
        """Calculate cosine similarity between vectors"""
        return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

    def institution_search(self, query: str, top_n: int = 10):
        # 1. Get all embeddings and calculate similarities
        df = WnTextEmbedding.get_embedding(content_type="institution")
        query_embedding = EmbeddingService.get_model().encode([query])[0]

        df["similarity"] = df["embedding"].apply(
            lambda x: self._cosine_similarity(np.array(x), query_embedding)
        )

        combined_results = df.sort_values('similarity', ascending=False).head(top_n * 2)
        institution_ids = combined_results['object_id'].tolist()
        # Create a Case/When expression to maintain the order
        ordering_cases = Case(
            *[When(pk=obj_id, then=Value(idx)) for idx, obj_id in enumerate(institution_ids)],
            output_field=IntegerField()
        )

        # Query the institutions and order them using MySQL
        institutions = WnInstitution.objects.select_related("state", "district").filter(
            pk__in=institution_ids).order_by(ordering_cases)
        for institution in institutions:
            print(f"{institution.institution_name}, {institution.state.name}, {institution.district.name}")
        return

    def course_search(self, query: str, top_n: int = 10):
        # 1. Get all embeddings and calculate similarities
        df = WnTextEmbedding.get_embedding(content_type="course")
        query_embedding = EmbeddingService.get_model().encode([query])[0]

        df["similarity"] = df["embedding"].apply(
            lambda x: self._cosine_similarity(np.array(x), query_embedding)
        )

        combined_results = df.sort_values('similarity', ascending=False).head(top_n * 2)
        course_ids = combined_results['object_id'].tolist()
        # Create a Case/When expression to maintain the order
        ordering_cases = Case(
            *[When(pk=obj_id, then=Value(idx)) for idx, obj_id in enumerate(course_ids)],
            output_field=IntegerField()
        )

        # Query the courses and order them using MySQL
        courses = WnCourse.objects.select_related('stream', 'degree').filter(pk__in=course_ids).order_by(ordering_cases)
        for course in courses:
            print(f"{course.course_name}, {course.stream.stream_name}, {course.degree.degree_name}")
        return
