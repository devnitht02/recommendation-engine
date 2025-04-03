from django.urls import path

from . import views
from .views import user_profile, signup, signin, signout, update_user_profile, google_login

urlpatterns = [
    path('user_profile', user_profile, name="user_profile"),

    path('update_user_profile', update_user_profile, name='update_user_profile'),

    path('signup/', signup, name='signup'),

    path('signin/', signin, name='signin'),


    path('google-login/', views.google_login, name='google-login'),

    path('signout/', signout, name='signout'),
    path('district-list/<int:state_id>/', views.get_district, name='district_list'),

]
