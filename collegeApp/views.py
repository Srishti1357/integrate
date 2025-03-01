
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student,  CustomUser
from adminApp.models import College


def user_login(request):
    """Login page where users enter only username and password."""
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        print(user)  # ✅ Debugging: Print user object

        if user is not None:
            if hasattr(user, 'college') and user.college:  # ✅ Ensure user has a college assigned
                login(request, user)
                return redirect("dashboard")
            else:
                return render(request, "login_college.html", {"error": "No college assigned to this user!"})
        return render(request, "login_college.html", {"error": "Invalid username or password!"})

    return render(request, "login_college.html")

@login_required
def dashboard(request):
    """Show only students from the logged-in user's college."""
    students = Student.objects.filter(college=request.user.college)
    return render(request, "dashboard_college.html", {"students": students})

@login_required
def update_approval(request, student_id, status):
    """Update student approval status."""
    student = get_object_or_404(Student, id=student_id)
    student.approval = status
    student.save()
    return redirect("dashboard")

def user_logout(request):
    """Log out the user."""
    logout(request)
    return redirect("login")
