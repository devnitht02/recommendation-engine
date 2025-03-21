import profile

from django.urls import path
from .views import user, signup, signin, signout,profile

urlpatterns = [
    path('users', user, name="users"),

    path('signup/', signup, name='signup'),

    path('profile/', profile, name='profile'),

    path('signin/', signin, name='signin'),

    path('signout/', signout, name='signout'),

]
