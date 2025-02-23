from .views import signin
from .views import signup
from django.urls import path

app_name = 'registration'

urlpatterns = [
    path('signup/', signup, name='signup'),

    path('signin/', signin, name='signin'),
]