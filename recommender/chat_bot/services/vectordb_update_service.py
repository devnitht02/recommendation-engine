import pandas as pd
import uuid
from django.db.models import F
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from institutions.models import WnInstitution


class VectorDbDataService:
    def get_data(self):
        data = WnInstitution.objects.select_related(
            "state", "district", "wninstitutioncourse", "wninstitutioncourse__course",
            "wninstitutioncourse__course__stream", "wninstitutioncourse__course__degree"
        ).filter(active=1).values(
            "id", "institution_name", "website",
            state_name=F("state__name"),
            district_name=F("district__name"),
            course_id=F("wninstitutioncourse__course__pk"),
            course_name=F("wninstitutioncourse__course__course_name"),
            stream_name=F("wninstitutioncourse__course__stream__stream_name"),
            degree_name=F("wninstitutioncourse__course__degree__degree_name"),
            degree_description=F("wninstitutioncourse__course__degree__degree_description")
        )
        return pd.DataFrame(list(data))

    def get_payload(self):
        institution_df = self.get_data()
        payload = []

        grouped = institution_df.groupby(['id', 'institution_name', 'website', 'state_name', 'district_name'])

        for (id, institution_name, website, state_name, district_name), group in grouped:
            institution = {
                "institution_id": id,
                "name": institution_name,
                "website": website,
                "state": state_name,
                "district": district_name,
                "courses": []
            }

            for _, row in group.iterrows():
                course = {
                    "course_id": row["course_id"],
                    "course_name": row['course_name'],
                    "stream": row['stream_name'],
                    "degree": row['degree_name'],
                    "degree_description": row['degree_description']
                }
                institution["courses"].append(course)

            payload.append(institution)

        return payload

    def __update_vector_db(self, payload: list):
        client = QdrantClient(host="localhost", port=6333)
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # Create a new collection
        collection_name = "institutions_courses"
        embedding_dimension = 384
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_dimension, distance=Distance.COSINE),
        )

        record_updated = 0
        # Add state and district embeddings to Qdrant
        for row in payload:
            # Combine relevant text for embedding
            text = f"institution: {row['name']}, state : {row['state']}, district: {row['district']}, "
            text += "Courses: " + ", ".join(
                f"{c['course_name']} ({c['stream']})"
                for c in row.get("courses", [])
            )

            embedding = model.encode(text)
            client.upsert(
                collection_name=collection_name,
                points=[{
                    "id": str(uuid.uuid4()),
                    "vector": embedding.tolist(),
                    "payload": {
                        "institution_id": int(row["institution_id"]),
                        "institution_name": row['name'],
                        "state_name": row['state'],
                        "district_name": row['district'],
                        "courses": row.get("courses", []),
                        "type": "institution"
                    }
                }]
            )
            record_updated += 1
            print(f"record : {record_updated} updated successfully")

    @classmethod
    def start(cls):
        try:
            self = cls()
            payload = self.get_payload()
            self.__update_vector_db(payload)
            print(f"*** Data Updated Successfully ***")

        except Exception as e:
            print(f"Failed to update data in vector DB")
            print(f"Error : {str(e)}")
