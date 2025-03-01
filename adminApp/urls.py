from django.urls import path
from .views import (
    admin_dashboard, college_list, college_create, college_delete,
    user_list, user_create, user_delete, student_list, student_create, student_delete,
    admin_login, admin_logout, toggle_college, print_students, student_update, user_update
)

urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # College URLs
    path('colleges/', college_list, name='college_list'),
    path('colleges/create/', college_create, name='college_create'),
    path('colleges/delete/<int:college_id>/', college_delete, name='college_delete'),
    path('colleges/toggle/<int:college_id>/', toggle_college, name='toggle_college'),  # ✅ Add this


    # User URLs
    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_create'),
    path('users/delete/<int:user_id>/', user_delete, name='user_delete'),
    # ... other URL patterns ...
    path('users/update/<int:user_id>/', user_update, name='user_update'),


    # Student URLs
    path('students/', student_list, name='student_list'),
    path('students/create/', student_create, name='student_create'),
    path('students/delete/<uuid:student_id>/', student_delete, name='student_delete'),
    path('students/print/', print_students, name='print_students'),
    path('students/update/<uuid:student_id>/', student_update, name='student_update'),

    # Authentication
    path('', admin_login.as_view(), name='admin_login'),
    path('logout/', admin_logout, name='admin_logout'),
]
