from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("college/", include("collegeApp.urls")),
    path('gate/', include('gate.urls')),
]
