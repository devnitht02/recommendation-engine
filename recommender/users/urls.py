from django.conf.urls.static import static
from django.urls import path

from recommender import settings
from . import views
from .views import user_profile, signup, signin, signout, update_user_profile

urlpatterns = [
                  path('user_profile', user_profile, name="user_profile"),

                  path('update_user_profile', update_user_profile, name='update_user_profile'),

                  path('signup/', signup, name='signup'),

                  path('signin/', signin, name='signin'),

                  path('google-login/', views.google_login, name='google-login'),

                  path('signout/', signout, name='signout'),

                  path('district-list/<int:state_id>/', views.get_district, name='district_list'),

                  path('upload_profile_picture/', views.upload_profile_picture, name='upload_profile_picture'),

                  path('reset_password_form/', views.forgot_password, name='forgot_password'),

                  path('new_password/', views.reset_password, name='reset_password'),

                  path('google-callback/', views.google_auth_callback, name='google_callback'),


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
