from django.urls import path

from institutions.views import view_course, view_institution
from . import views
from .views import dashboard, contact_page, about

urlpatterns = [
    path('', dashboard, name="dashboard"),

    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),

    path('next_page/<int:item_id>/', views.redirect_to_item, name='redirect_to_item'),

    path('course/<int:course_id>/', view_course, name='course_view'),

    path('institution/<int:institution_id>/', view_institution, name='institution_view'),

    path('contact.html', contact_page, name='contact_page'),

    path('about.html', about, name='about_page'),
]
