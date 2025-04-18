from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, ChangePasswordView, ProfileView,
    PasswordResetRequestView, PasswordResetConfirmView,
    EmailVerificationView, UserViewSet
)

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('email-verify/<str:token>/', EmailVerificationView.as_view(), name='email-verify'),
    path('', include(router.urls)),
]