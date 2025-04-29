import pandas as pd
from users.models import WnUser
from institutions.models import WnCourse, WnStreamChoice, WnLocationChoice
from recommendations.services.recommendation_service import RecommendationService
from recommendations.services.course_collaborative import CourseCollaborative
from sklearn.preprocessing import MinMaxScaler
from django.db.models import F, Case, When, Value, IntegerField


class CourseHybrid:

    def get_user_data(self, user_id):
        user = WnUser.objects.filter(pk=user_id).first()
        data = {
            "user_name": user.user_name,

        }
        if hasattr(user, "state"):
            data["state_name"] = user.state.name

        if hasattr(user, "district"):
            data["state_name"] = user.district.name

        stream_choice = WnStreamChoice.objects.filter(user_id=user_id).first()
        if stream_choice:
            data["stream_choice"] = stream_choice.stream.stream_name

        location_choice = WnLocationChoice.objects.filter(user_id=user)
        data["state_choice"] = []
        data["district_choice"] = []

        for choice in location_choice:
            data["state_choice"].append(choice.state.name)
            data["district_choice"].append(choice.district.name)

        return data

    def recommend(self, user_id, top_n):
        data = self.get_user_data(user_id)

        query = data.get("stream_choice", "")

        ins = RecommendationService()
        results = ins.recommend_course(query, top_n)

        results.rename(columns={"object_id": "course_id", "similarity": "cb_score"}, inplace=True)
        cb_df = results[['course_id', 'cb_score']]

        collab = CourseCollaborative()
        cf_df = collab.recommend(user_id, top_n)
        if cf_df.empty:
            return cb_df

        hybrid_df = pd.merge(cb_df, cf_df, on="course_id", how="outer")
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

    def get_hybrid_courses(self, user_id, top_n=10):
        recommended_df = self.recommend(user_id, top_n)
        course_ids = recommended_df['course_id'].tolist()
        # Create a Case/When expression to maintain the order
        ordering_cases = Case(
            *[When(pk=obj_id, then=Value(idx)) for idx, obj_id in enumerate(course_ids)],
            output_field=IntegerField()
        )

        # Query the courses and order them using MySQL
        courses = WnCourse.objects.filter(
            pk__in=course_ids).order_by(ordering_cases)

        return courses
