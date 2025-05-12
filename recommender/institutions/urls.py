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

    path('remove_favourite/', views.remove_favourite, name='remove_favourite'),
    path('select-course/', views.course_selection_form, name='select_course_form'),
    path('get-districts/<int:state_id>/', views.get_districts, name='get_districts'),
    path('get-institutions/<int:state_id>/<int:district_id>/', views.get_institutions, name='get_institutions'),
    path('get-courses/<int:institution_id>/', views.get_courses, name='get_courses'),





    path('like-institution/', views.like_institution, name='like_institution'),

    path('like-course/', views.like_course, name='like_course'),
]
