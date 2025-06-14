from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient  #pip install qdrant_client
from qdrant_client.models import VectorParams, Distance, PointStruct
from groq import Groq
import pandas as pd
from transformers import pipeline
from recommender.settings import CHATBOT_APIKEY
import uuid

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)
# Load the zero-shot-classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


class ChatBotService:

    def is_course_or_institution_related(self, prompt: str) -> bool:
        labels = ["education", "technology", "sports", "finance", "college", "institution", "courses", "others"]
        result = classifier(prompt, labels)

        # for label, score in zip(result['labels'], result['scores']):
        #     print(f"{label}: {score:.4f}")
        return result['labels'][0] != labels[-1]

    def __get_vector_data(self, user_prompt):
        query_embedding = model.encode(user_prompt)
        results = client.search(
            collection_name="institutions_courses",
            query_vector=query_embedding.tolist(),
            limit=10
        )
        context_chunks = [
            f"institution_name: <a href='/view_institution/{r.payload['institution_id']}'>{r.payload['institution_name']}</a>, "
            f"district_name: {r.payload['district_name']}, state_name: {r.payload['state_name']}, " +
            ", ".join([
                f"course_name: <a href='/view_course/{course['course_id']}/'>{course['degree']}. {course['course_name']} ({course['degree_description']})</a>, "
                f"stream: {course['stream']}"
                for course in r.payload["courses"]
            ])
            for r in results
        ]

        context = "\n".join(context_chunks)
        return context

    def __add_instructions(self, context, user_prompt):
        result_prompt = f"""
        [INST]
        You are a helpful assistant. When providing institution and course details,
        **include all URLs exactly as given without removing or modifying**.
        **If the response includes multiple courses or institutions, format it as an HTML ordered list. **.

        Context:
        {context}

        Question:
        {user_prompt}
        """
        return result_prompt

    def __llm(self, prompt):
        groq_client = Groq(
            # The default api key
            api_key=CHATBOT_APIKEY,
        )

        messages = [
            {"role": "system", "content": "You are a helpful assistant specialized in education-related queries. "},
            {"role": "user", "content": prompt}
        ]
        messages.append({
            "role": "system",
            "content": (
                "If the response includes multiple courses or institutions, format it as an HTML ordered list. "
                "Otherwise, give a short, clear answer."
            )
        })

        # Create chat completion
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192",  # The supported model in Groq
        )

        # Print the result
        return chat_completion.choices[0].message.content

    @classmethod
    def chat(cls, user_prompt):
        self = cls()
        if (self.is_course_or_institution_related(user_prompt)):
            vector_data = self.__get_vector_data(user_prompt)
            prompt = self.__add_instructions(vector_data, user_prompt)
            return self.__llm(prompt)

        return "Sorry, I can only assist with education-related topics such as courses, institutions, and admissions. 😊"
