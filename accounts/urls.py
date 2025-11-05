from django.urls import path
from .views import SignupView, VerifyOTPView, LoginView

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("login/", LoginView.as_view()),
]
