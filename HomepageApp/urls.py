from django.urls import path
from django.shortcuts import render
from .views import send_otp, verify_otp, resend_otp, generate_qr_code, upload_image, verify_ocr, qr_display
from . import views

urlpatterns = [
    path("", send_otp, name="send_otp"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("resend-otp/", resend_otp, name="resend_otp"),
    path("signup/", views.student_form, name="signup"),
     path('generate_qr_code/<int:student_id>/', generate_qr_code, name='generate_qr_code'),  # QR code generation
    path('upload-image/',upload_image ),
    path('verify-ocr/', verify_ocr, name='verify_ocr'),
    path('qr_display/', qr_display, name='qr_display'),
]