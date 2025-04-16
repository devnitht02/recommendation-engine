from django.urls import path

from . import views
from .views import institutions, view_institution

urlpatterns = [
    path('institutions/', institutions, name='institutions'),

    path('courses/', views.courses, name='courses'),

    path('view_institution/<int:institution_id>', view_institution, name='view_institution'),

    path('view_course/<int:course_id>/', views.view_course, name='view_course'),

    path('favourites/', views.favourites, name='favourites'),

    path('search_suggestions_courses/', views.search_suggestions_courses, name='search_suggestions_courses'),

    path('search_suggestions_institutions/', views.search_suggestions_institutions,
         name='search_suggestions_institutions'),
    path('toggle_favourite/', views.toggle_favourite, name='toggle_favourite'),

]
