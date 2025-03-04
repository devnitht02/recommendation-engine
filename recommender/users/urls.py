from django.urls import path
from .views import user, signup, signin, signout

urlpatterns = [
    path('users', user, name="users"),

    path('signup/', signup, name='signup'),

    path('signin/', signin, name='signin'),

    path('signout/', signout, name='signout'),

]
