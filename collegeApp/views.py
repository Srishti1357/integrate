# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.utils.dateparse import parse_date
# from .models import Visitor
# from django.shortcuts import render
# from .models import Visitor
# from .filters import VisitorFilter
# # def visitor_list(request):
# #     visitors = Visitor.objects.all()
# #     return render(request, "visitor_list.html", {"visitors": visitors})




# # def visitor_list(request):
# #     visitors = Visitor.objects.all()
# #     visitor_filter = VisitorFilter(request.GET, queryset=visitors)  # Apply filters
# #     print(visitor_filter.qs[0].name)
# #     return render(request, "visitor_list.html", {"visitors": visitor_filter.qs, "visitor_filter": visitor_filter})

# from django.shortcuts import render
# from .models import Visitor
# from .filters import VisitorFilter

# def visitor_list(request):
#     visitors = Visitor.objects.all()
#     visitor_filter = VisitorFilter(request.GET, queryset=visitors)  # Apply filters
    
#     # ✅ Sorting filtered visitors by datetime (newest first)
#     sorted_visitors = sorted(visitor_filter.qs, key=lambda v: v.datetime, reverse=True)

#     return render(request, "visitor_list.html", {"visitors": sorted_visitors, "visitor_filter": visitor_filter})


# def update_approval(request, visitor_id, status):
#     visitor = Visitor.objects.get(id=visitor_id)
#     visitor.approval = status
#     visitor.save()
#     return JsonResponse({"status": "success", "approval": visitor.approval_status()})


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
