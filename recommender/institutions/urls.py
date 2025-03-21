from django.urls import path

from . import views
from .views import institutions, view_course, view_institution

urlpatterns = [
    path('institutions', institutions, name='institutions'),

    path('courses', views.courses, name='courses'),

    path('view_institution', view_institution, name='view_institution'),

    path('view_course/<int:course_id>/', views.view_course, name='view_course'),


]
