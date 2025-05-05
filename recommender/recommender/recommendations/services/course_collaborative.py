import os

# For ML
import joblib
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder

# For Data
from institutions.models import WnCourseChoice, WnSelectedCourse

class CourseCollaborative:

    def get_course_choice(self):
        data = WnCourseChoice.objects.filter(active=1).values("user_id","course_id")
        return pd.DataFrame(list(data))
    
    def get_selected_course(self):
        data = WnSelectedCourse.objects.filter(active=1).values("user_id","course_id")
        return pd.DataFrame(list(data))

    def train_svd_model(self):
        choices_df = self.get_course_choice()
        selected_df = self.get_selected_course()

        """ Encode user_id and course_id to indices """

        user_encoder = LabelEncoder()
        course_encoder = LabelEncoder()

        # Fit encoders on the union of both tables
        user_encoder.fit(pd.concat([choices_df['user_id'], selected_df['user_id']]))
        course_encoder.fit(pd.concat([choices_df['course_id'], selected_df['course_id']]))

        # Transform
        choices_df['user_idx'] = user_encoder.transform(choices_df['user_id'])
        choices_df['course_idx'] = course_encoder.transform(choices_df['course_id'])

        selected_df['user_idx'] = user_encoder.transform(selected_df['user_id'])
        selected_df['course_idx'] = course_encoder.transform(selected_df['course_id'])

        """ Create interaction matrix with different weights """
        n_users = len(user_encoder.classes_)
        n_courses = len(course_encoder.classes_)

        interaction_matrix = np.zeros((n_users, n_courses))

        # Add interested courses with weight 1
        for row in choices_df.itertuples():
            interaction_matrix[row.user_idx, row.course_idx] = 1

        # Overwrite with stronger weight if selected
        for row in selected_df.itertuples():
            interaction_matrix[row.user_idx, row.course_idx] = 10 

        """ Apply TruncatedSVD """
        svd = TruncatedSVD(n_components=5, random_state=42)
        user_latent = svd.fit_transform(interaction_matrix)
        course_latent = svd.components_.T
        
        numpy_dir = "ml_files/numpy"
        os.makedirs(numpy_dir, exist_ok=True)

        pkl_dir = "ml_files/pkl"
        os.makedirs(pkl_dir, exist_ok=True)
        # Save new files (overwrite if exists)
        np.save('ml_files/numpy/user_latent.npy', user_latent)
        np.save('ml_files/numpy/course_latent.npy', course_latent)
        np.save("ml_files/numpy/interaction_matrix.npy", interaction_matrix)

        joblib.dump(course_encoder, "ml_files/pkl/course_encoder.pkl")
        joblib.dump(user_encoder, "ml_files/pkl/user_encoder.pkl")

    def load_or_train(self):
        try:
            # Try loading the files
            user_latent = np.load('ml_files/numpy/user_latent.npy')
            course_latent = np.load('ml_files/numpy/course_latent.npy')
            interaction_matrix = np.load('ml_files/numpy/interaction_matrix.npy')

            course_encoder = joblib.load("ml_files/pkl/course_encoder.pkl")
            user_encoder = joblib.load("ml_files/pkl/user_encoder.pkl")
            print("Loaded precomputed latent matrices.")
        except FileNotFoundError:
            print("Latent matrices not found. Training model...")
            self.train_svd_model()

            # Retry loading after training
            user_latent = np.load('ml_files/numpy/user_latent.npy')
            course_latent = np.load('ml_files/numpy/course_latent.npy')
            interaction_matrix = np.load('ml_files/numpy/interaction_matrix.npy')

            course_encoder = joblib.load("ml_files/pkl/course_encoder.pkl")
            user_encoder = joblib.load("ml_files/pkl/user_encoder.pkl")
            print("Model trained and latent matrices loaded.")

        return user_latent, course_latent, interaction_matrix, course_encoder, user_encoder
    

    def recommend(self,user_id,top_n = 5):
        user_latent, course_latent, interaction_matrix, course_encoder, user_encoder = self.load_or_train()

        try:
            user_index = user_encoder.transform([user_id])[0]

            scores = np.dot(user_latent[user_index], course_latent.T)

            # Remove courses the user already interacted with
            already_seen = np.where(interaction_matrix[user_index] > 0)[0]
            scores[already_seen] = -np.inf

            # Get top 5 course indices
            top_n_indices = scores.argsort()[::-1][:top_n]

            top_courses = course_encoder.inverse_transform(top_n_indices)
            top_scores = scores[top_n_indices]
            return pd.DataFrame({
                        "course_id": top_courses,
                        "cf_score": top_scores
                    })

        except Exception as e:
            return pd.DataFrame({})