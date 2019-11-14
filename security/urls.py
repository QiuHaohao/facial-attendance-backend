from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from .views import current_user, SignUpView

urlpatterns = [
    path('token/', obtain_jwt_token, name='token'),
    path('refresh/', refresh_jwt_token, name='token_refresh'),
    path('verify/', verify_jwt_token, name='token_verify'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('current/', current_user, name='current_user'),
]
