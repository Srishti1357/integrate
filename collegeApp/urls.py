from django.urls import path
from .views import visitor_list, update_approval

urlpatterns = [
    path("", visitor_list, name="visitor_list"),
    path("update-approval/<int:visitor_id>/<int:status>/", update_approval, name="update_approval"),
]
