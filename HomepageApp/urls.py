from django.urls import path
from django.shortcuts import render
from .views import send_otp, verify_otp, resend_otp

urlpatterns = [
    path("", send_otp, name="send_otp"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("resend-otp/", resend_otp, name="resend_otp"),  
    path("login", lambda request: render(request, "student_login.html"), name="login"),
    path("signup/", lambda request: render(request, "student_signup.html"), name="signup"),
]