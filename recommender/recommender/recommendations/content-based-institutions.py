from urllib.parse import quote_plus
import pandas as pd
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from django.conf import settings
# import pymysql

from institutions.models import WnInstitution

# Load Sentence Transformer Model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Ensure you're using the correct model


# Load institution data using Django ORM
def load_institution_data():
    # Fetch all institution records from the database
    institutions = WnInstitution.objects.all().values("institution_name", "institution_type", "state", "district",
                                                      "embeddings")

    # Convert ORM QuerySet to Pandas DataFrame
    df = pd.DataFrame(list(institutions))

    # Convert embeddings from string (stored in DB) to Python lists
    df["embeddings"] = df["embeddings"].apply(eval)  # Ensure JSON-safe conversion

    return df


# Recommendation function
def recommend_institutions(input_text, top_n=5):
    df = load_institution_data()  # Load data from MySQL
    input_embedding = model.encode([input_text])

    # Compute similarity
    df["similarity"] = df["embeddings"].apply(lambda x: cosine_similarity([x], input_embedding)[0][0])

    # Sort and return top matches
    recommendations = df.sort_values(by="similarity", ascending=False).head(top_n)
    return recommendations[["institution_name", "institution_type", "state", "district", "similarity"]]
