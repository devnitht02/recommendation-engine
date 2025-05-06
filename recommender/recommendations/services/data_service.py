import pandas as pd
from typing import Dict, List
from institutions.models import WnInstitutionCourse, WnCourse
from .embedding_service import EmbeddingService
from recommendations.models import WnTextEmbedding

class BaseDataService:
    """Base class with common DataFrame conversion functionality"""
    @staticmethod
    def _queryset_to_dataframe(queryset, field_map: Dict = None) -> pd.DataFrame:
        """
        Convert Django queryset to pandas DataFrame with optional field renaming
        
        Args:
            queryset: Django queryset
            field_map: Dictionary mapping model fields to output columns
            
        Returns:
            pd.DataFrame containing the queryset data
        """
        if field_map:
            data = queryset.values(*field_map.keys())
            df = pd.DataFrame.from_records(data)
            df.rename(columns=field_map, inplace=True)
        else:
            df = pd.DataFrame.from_records(queryset.values())
        return df
    
    @staticmethod
    def _concat_series(series):
        return ', '.join(sorted(set(series.dropna().astype(str).str.strip())))
    
class InstitutionDataService(BaseDataService):
    """Handles institution and course data fetching and preprocessing"""
    def get_institution_features(self) -> pd.DataFrame:
        queryset = WnInstitutionCourse.objects.select_related(
            'institution','institution__state','institution__district',
            'course','course__stream','course__degree'
        ).filter()

        field_map = {
            'institution__pk' : "institution_id",
            "institution__institution_name" : "institution_name",
            "institution__state__name" : "state",
            "institution__district__name" : "district",
            "course__course_description" : "course_description",
            "course__degree__degree_name" : "degree_name",
            "course__degree__degree_description" : "degree_description",
            "course__stream__stream_name" : "stream_name",
            "course__course_name" : "course_name"
        }

        df = self._queryset_to_dataframe(queryset, field_map)
        return self._preprocess_institution_features(df)

    def _preprocess_institution_features(self, df: pd.DataFrame) -> pd.DataFrame:

        df["institution_type"] = df["institution_name"].apply(self._get_institution_type)
        df_grouped = df.groupby(["institution_id","institution_name"]).agg({
            "institution_type":"max",
            "state":"max",
            "district":"max",
            "course_description":self._concat_series,
            "degree_description":self._concat_series,
            "degree_name":self._concat_series,
            "stream_name":self._concat_series,
            "course_name":self._concat_series
        })
        df_grouped = df_grouped.reset_index()
        df_grouped[["institution_name","degree_description","course_name"]].loc[0]

        df_grouped["combined_text"] = self._create_combined_text(df_grouped)
        return df_grouped

    def _create_combined_text(self, df: pd.DataFrame) -> pd.Series:
        """Combine relevant text fields for embedding"""
        return df[
            ["institution_name", "institution_type", "state", "district", 
            "course_description", "degree_description", "degree_name", 
            "stream_name", "course_name"]
        ].astype(str).agg(" ".join, axis=1)


    def _get_institution_type(self,institution_name):
        for word in institution_name.split(" "):
            if word.lower() in ["government","indian","central"]:
                return "public"
            else:
                return "private"
            
    def start(self):
        df = self.get_institution_features()
        df["embeddings"] = df["combined_text"].apply(lambda x: EmbeddingService.generate_embeddings(x))
        embeddings_data = [
            {
                'content_type': 'institution',
                'object_id': row['institution_id'],
                'text': row['combined_text'],
                'embedding': row['embeddings'],
                'model_version': 'all-MiniLM-L6-v2'
            }
            for _, row in df.iterrows()
        ]

        WnTextEmbedding.bulk_store_embeddings(embeddings_data)
        print("Embedding saved successfull")


class CourseDataService(BaseDataService):
    """Handles course data fetching and preprocessing"""
    def get_course_features(self) -> pd.DataFrame:
        queryset = WnCourse.objects.select_related(
            'stream','degree'
        ).filter()

        field_map = {
            'pk' : "course_id",
            "course_name" : "course_name",
            "course_description" : "course_description",
            "degree__degree_name" : "degree_name",
            "degree__degree_description" : "degree_description",
            "stream__stream_name" : "stream_name",
        }

        df = self._queryset_to_dataframe(queryset, field_map)
        return self._preprocess_course_features(df)

    def _preprocess_course_features(self, df: pd.DataFrame) -> pd.DataFrame:

        df["combined_text"] = self._create_combined_text(df)
        return df

    def _create_combined_text(self, df: pd.DataFrame) -> pd.Series:
        """Combine relevant text fields for embedding"""
        return df[
            [
                "course_name", "course_description", "degree_description",
                "degree_name", "stream_name"
            ]
        ].astype(str).agg(" ".join, axis=1)

            
    def start(self):
        df = self.get_course_features()
        print(df.head())
        df["embeddings"] = df["combined_text"].apply(lambda x: EmbeddingService.generate_embeddings(x))
        embeddings_data = [
            {
                'content_type': 'course',
                'object_id': row['course_id'],
                'text': row['combined_text'],
                'embedding': row['embeddings'],
                'model_version': 'all-MiniLM-L6-v2'
            }
            for _, row in df.iterrows()
        ]

        WnTextEmbedding.bulk_store_embeddings(embeddings_data)
        print("Embedding saved successfull")