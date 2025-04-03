from django.urls import path
from . import views
from .views import dashboard
from institutions.views import view_course, view_institution

urlpatterns = [
    path('', dashboard, name="dashboard"),

    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),

  path('next_page/<int:item_id>/', views.redirect_to_item, name='redirect_to_item'),  # New path for redirection

    # Your existing URLs for course and institution views:
    path('course/<int:course_id>/', view_course, name='course_view'),


    path('institution/<int:institution_id>/', view_institution, name='institution_view'),
]





