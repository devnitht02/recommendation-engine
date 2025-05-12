# search_utils.py
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk
# nltk.download('stopwords')

class SearchEngine:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.stemmer = PorterStemmer()
        self.stopwords = set(stopwords.words('english'))
        self.institution_data = None
        self.course_data = None
        self.bm25_index = None
        self.embeddings = None
    
    def initialize(self):
        """Load or create search indices"""
        from institutions.models import WnInstitution, WnCourse
        
        # Load all institutions and courses
        institutions = WnInstitution.objects.select_related("state","district").all()
        courses = WnCourse.objects.select_related("degree","stream").all()
        
        # Prepare data
        self.institution_data = [
            {
                'id': f'inst_{i.id}', 
                'text': f'{i.institution_name} {i.state.name} {i.district.name}', 
                'type' : 'institution',
                'obj': i
            }
            for i in institutions
        ]
        self.course_data = [
            {
                'id': f'course_{c.id}', 
                'text': f'{c.course_name} {c.stream.stream_name} {c.degree.degree_name} {c.degree.degree_description}',
                'type' : 'course',
                'obj': c
            }
            for c in courses
        ]
        
        all_docs = [item['text'] for item in self.institution_data + self.course_data]
        
        # Create BM25 index
        tokenized_docs = [self._tokenize(doc) for doc in all_docs]
        self.bm25_index = BM25Okapi(tokenized_docs)
        
        # Create embeddings (load if exists, otherwise create)
        try:
            self.embeddings = np.load('search_embeddings.npy')
        except:
            self.embeddings = self.model.encode(all_docs)
            np.save('search_embeddings.npy', self.embeddings)
    
    def _tokenize(self, text):
        tokens = []
        for token in text.lower().split():
            token = token.strip(".,!?;:\"'()[]{}")
            if token and token not in self.stopwords:
                tokens.append(self.stemmer.stem(token))
        return tokens
    
    def search(self, query, alpha=0.5, top_n=10):
        """Hybrid search combining BM25 and semantic search"""
        all_data = self.institution_data + self.course_data
        
        # BM25 search
        tokenized_query = self._tokenize(query)
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        bm25_scores = self._normalize_scores(bm25_scores)
        
        # Semantic search
        query_embedding = self.model.encode([query])
        semantic_scores = np.dot(self.embeddings, query_embedding.T).flatten()
        semantic_scores = self._normalize_scores(semantic_scores)
        
        # Combine scores
        combined_scores = {}
        for idx, (bm25_score, semantic_score) in enumerate(zip(bm25_scores, semantic_scores)):
            combined_scores[idx] = alpha * bm25_score + (1 - alpha) * semantic_score
        
        # Get top results
        sorted_indices = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)[:top_n]
        
        # Prepare results
        results = []
        for idx in sorted_indices:
            item = all_data[idx]
            if item['id'].startswith('inst_'):
                results.append({
                    'id' : item['obj'].pk,
                    'type': 'institution',
                    'score': int(combined_scores[idx]),
                    'name': item['obj'].institution_name,
                    'state' : item['obj'].state.name,
                    'district' : item['obj'].district.name
                })
            else:
                results.append({
                    'id' : item['obj'].pk,
                    'type': 'course',
                    'score': int(combined_scores[idx]),
                    'name': item['obj'].course_name,
                    'degree_name' : item['obj'].degree.degree_name,
                    'degree_description' : item['obj'].degree.degree_description
                })
        
        return results
    
    def _normalize_scores(self, scores):
        """Normalize scores to 0-1 range"""
        if len(scores) == 0:
            return scores
        min_score, max_score = min(scores), max(scores)
        if max_score == min_score:
            return [0.5] * len(scores)
        return [(s - min_score) / (max_score - min_score) for s in scores]

# Singleton instance
search_engine = SearchEngine()