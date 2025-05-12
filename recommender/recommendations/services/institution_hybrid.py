import pandas as pd
from users.models import WnUser
from institutions.models import WnInstitution, WnStreamChoice, WnLocationChoice, WnInstitutionChoice
from recommender.models import WnFavourite
from recommendations.services.recommendation_service import RecommendationService
from recommendations.services.institution_collaborative import InstitutionCollaborative
from sklearn.preprocessing import MinMaxScaler
from django.db.models import F, Case, When, Value, IntegerField, Prefetch


class InstitutionHybrid:

    def get_user_data(self, user_id):

        user = WnUser.objects.filter(pk=user_id).first()
        data = {
            "user_name": user.user_name,
            "stream" : user.stream
        }
        if hasattr(user, "state"):
            data["state_name"] = user.state.name

        if hasattr(user, "district"):
            data["state_name"] = user.district.name

        stream_choice = WnStreamChoice.objects.filter(user_id=user_id).first()
        if stream_choice:
            data["stream_choice"] = stream_choice.stream.stream_name

        data["institution_choice"] = []
        institution_choice = WnInstitutionChoice.objects.select_related("institution","institution__state","institution__district").filter(user_id = user_id,active='1')
        for institution in institution_choice:
            data["institution_choice"].append(f"{institution.institution.institution_name} {institution.institution.state.name} {institution.institution.district.name}")

        location_choice = WnLocationChoice.objects.filter(user_id=user)
        data["state_choice"] = []
        data["district_choice"] = []

        for choice in location_choice:
            data["state_choice"].append(choice.state.name)
            data["district_choice"].append(choice.district.name)

        data["favourite_institutions"] = []
        favourite_institutions = WnFavourite.objects.select_related("institution","institution__state","institution__district").filter(user_id = user_id,institution__isnull = False)
        for institution in favourite_institutions:
            data["favourite_institutions"].append(f"{institution.institution.institution_name} {institution.institution.state.name} {institution.institution.district.name}")

        # queryset = WnUser.objects.filter(pk=user_id).values(
        #     "hsc_percentage",
        #     "user_gender", # LEFT JOIN
        #     stream_choice=F('wnstreamchoice__stream__stream_name'),  # LEFT JOIN
        #     state_choice=F('wnlocationchoice__state__name'),        # LEFT JOIN
        #     district_choice=F('wnlocationchoice__district__name'),   # LEFT JOIN
        # )
        return data

    def recommend(self, user_id, top_n):
        data = self.get_user_data(user_id)

        states = set(data["state_choice"])
        districts = set(data["district_choice"])

        query = data.get("stream_choice", "") + " ".join(
            f"{district}" for district in districts) + " ".join(f"{state}" for state in states)
        
        if data["stream"]:
            query += f' {data["stream"]} '

        if data["favourite_institutions"]:
            query += " ".join(f"{institution}" for institution in data["favourite_institutions"])

        if data["institution_choice"]:
            query += " ".join(f"{institution}" for institution in data["institution_choice"])

        ins = RecommendationService()
        results = ins.recommend_institution(query, top_n)

        results.rename(columns={"object_id": "institution_id", "similarity": "cb_score"}, inplace=True)
        cb_df = results[['institution_id', 'cb_score']]

        collab = InstitutionCollaborative()
        cf_df = collab.recommend(user_id, top_n)
        if cf_df.empty:
            return cb_df

        hybrid_df = pd.merge(cb_df, cf_df, on="institution_id", how="outer")
        # Fill missing scores with 0
        hybrid_df["cb_score"] = hybrid_df["cb_score"].fillna(0)
        hybrid_df["cf_score"] = hybrid_df["cf_score"].fillna(0)
        scaler = MinMaxScaler()
        hybrid_df["cb_score_scaled"] = scaler.fit_transform(hybrid_df["cb_score"].values.reshape(-1, 1)).flatten()
        hybrid_df["cf_score_scaled"] = scaler.fit_transform(hybrid_df["cf_score"].values.reshape(-1, 1)).flatten()

        # Combine using weights
        alpha = 0.4
        beta = 0.6
        hybrid_df["hybrid_score"] = alpha * hybrid_df["cb_score_scaled"] + beta * hybrid_df["cf_score_scaled"]

        # Sort and get Top-N
        top_hybrid = hybrid_df.sort_values("hybrid_score", ascending=False).head(top_n)
        return top_hybrid

    def get_hybrid_institutions(self, user_id, top_n=10):
        recommended_df = self.recommend(user_id, top_n)
        institution_ids = recommended_df['institution_id'].tolist()
        # Create a Case/When expression to maintain the order
        ordering_cases = Case(
            *[When(pk=obj_id, then=Value(idx)) for idx, obj_id in enumerate(institution_ids)],
            output_field=IntegerField()
        )

        # Query the institutions and order them using MySQL
        institutions = WnInstitution.objects.select_related("state", "district").filter(
            pk__in=institution_ids).order_by(ordering_cases)

        return institutions
