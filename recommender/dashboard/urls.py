from django.urls import path
from . import views
from .views import dashboard

urlpatterns = [
    path('', dashboard, name="dashboard"),

    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),

]
