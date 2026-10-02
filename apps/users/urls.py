from django.urls import path
from .views import (
    RegisterView,
    ProfileView,
    VerifyEmailView,
    PasswordResetRequestView,
    PasswordResetVerifyView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'users'

urlpatterns = [
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', VerifyEmailView.as_view(), name='verify'),
]