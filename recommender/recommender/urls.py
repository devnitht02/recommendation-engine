from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin Panel

    path('', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),

    path('', include(('users.urls', 'users'), namespace='users')),

    path('', include(('institutions.urls', 'institutions'), namespace='institutions')),


]
