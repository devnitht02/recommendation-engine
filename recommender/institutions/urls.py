from . import views
from .views import institutions
from django.urls import path


urlpatterns = [
    path('institutions', institutions, name='institutions'),

    path('courses', views.courses, name='courses'),


]