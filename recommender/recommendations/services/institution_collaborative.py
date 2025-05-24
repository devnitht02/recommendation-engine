import os

# For ML
import joblib
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder

# For Data
from institutions.models import WnInstitutionChoice, WnSelectedCourse


class InstitutionCollaborative:

    def get_institution_choice(self):
        data = WnInstitutionChoice.objects.filter(active=1).values("user_id", "institution_id")
        return pd.DataFrame(list(data))

    def get_selected_institution(self):
        data = WnSelectedCourse.objects.filter(active=1).values("user_id", "institution_id")
        return pd.DataFrame(list(data))

    def train_svd_model(self):
        choices_df = self.get_institution_choice()
        selected_df = self.get_selected_institution()

        """ Encode user_id and institution_id to indices """

        user_encoder = LabelEncoder()
        institution_encoder = LabelEncoder()

        # Fit encoders on the union of both tables
        user_encoder.fit(pd.concat([choices_df['user_id'], selected_df['user_id']]))
        institution_encoder.fit(pd.concat([choices_df['institution_id'], selected_df['institution_id']]))

        # Transform
        choices_df['user_idx'] = user_encoder.transform(choices_df['user_id'])
        choices_df['institution_idx'] = institution_encoder.transform(choices_df['institution_id'])

        selected_df['user_idx'] = user_encoder.transform(selected_df['user_id'])
        selected_df['institution_idx'] = institution_encoder.transform(selected_df['institution_id'])

        """ Create interaction matrix with different weights """
        n_users = len(user_encoder.classes_)
        n_institutions = len(institution_encoder.classes_)

        interaction_matrix = np.zeros((n_users, n_institutions))

        # Add interested institutions with weight 1
        for row in choices_df.itertuples():
            interaction_matrix[row.user_idx, row.institution_idx] = 1

        # Overwrite with stronger weight if selected
        for row in selected_df.itertuples():
            interaction_matrix[row.user_idx, row.institution_idx] = 10

        """ Apply TruncatedSVD """
        svd = TruncatedSVD(n_components=5, random_state=42)
        user_latent = svd.fit_transform(interaction_matrix)
        institution_latent = svd.components_.T

        numpy_dir = "ml_files/numpy"
        os.makedirs(numpy_dir, exist_ok=True)

        pkl_dir = "ml_files/pkl"
        os.makedirs(pkl_dir, exist_ok=True)
        # Save new files (overwrite if exists)
        np.save('ml_files/numpy/user_latent.npy', user_latent)
        np.save('ml_files/numpy/institution_latent.npy', institution_latent)
        np.save("ml_files/numpy/interaction_matrix.npy", interaction_matrix)

        joblib.dump(institution_encoder, "ml_files/pkl/institution_encoder.pkl")
        joblib.dump(user_encoder, "ml_files/pkl/user_encoder.pkl")

    def load_or_train(self):
        try:
            # Try loading the files
            user_latent = np.load('ml_files/numpy/user_latent.npy')
            institution_latent = np.load('ml_files/numpy/institution_latent.npy')
            interaction_matrix = np.load('ml_files/numpy/interaction_matrix.npy')

            institution_encoder = joblib.load("ml_files/pkl/institution_encoder.pkl")
            user_encoder = joblib.load("ml_files/pkl/user_encoder.pkl")
            print("Loaded precomputed latent matrices.")
        except FileNotFoundError:
            print("Latent matrices not found. Training model...")
            self.train_svd_model()

            # Retry loading after training
            user_latent = np.load('ml_files/numpy/user_latent.npy')
            institution_latent = np.load('ml_files/numpy/institution_latent.npy')
            interaction_matrix = np.load('ml_files/numpy/interaction_matrix.npy')

            institution_encoder = joblib.load("ml_files/pkl/institution_encoder.pkl")
            user_encoder = joblib.load("ml_files/pkl/user_encoder.pkl")
            print("Model trained and latent matrices loaded.")

        return user_latent, institution_latent, interaction_matrix, institution_encoder, user_encoder

    def recommend(self, user_id, top_n=5):
        user_latent, institution_latent, interaction_matrix, institution_encoder, user_encoder = self.load_or_train()

        try:
            user_index = user_encoder.transform([user_id])[0]

            scores = np.dot(user_latent[user_index], institution_latent.T)

            # Remove institutions the user already interacted with
            already_seen = np.where(interaction_matrix[user_index] > 0)[0]
            scores[already_seen] = -np.inf

            # Get top 5 institution indices
            top_n_indices = scores.argsort()[::-1][:top_n]

            top_institutions = institution_encoder.inverse_transform(top_n_indices)
            top_scores = scores[top_n_indices]
            return pd.DataFrame({
                "institution_id": top_institutions,
                "cf_score": top_scores
            })

        except Exception as e:
            print(f"collaborative error: {e}")
            return pd.DataFrame({})
