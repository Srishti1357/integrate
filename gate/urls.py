from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('qr/', views.qr, name='qr'),
    path('get-attendance/<str:roll_number>/', views.get_attendance, name='get_attendance'),
]