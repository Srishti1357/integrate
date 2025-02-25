from django.urls import path
from .views import user_login, dashboard, update_approval, user_logout

urlpatterns = [
    path("", user_login, name="login"),  # Login is now the home page
    path("dashboard/", dashboard, name="dashboard"),
    path("approve/<int:student_id>/<int:status>/", update_approval, name="update_approval"),
    path("logout/", user_logout, name="logout"),
]
