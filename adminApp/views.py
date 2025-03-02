from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from adminApp.models import College
from collegeApp.models import CustomUser, Student
from gate.models import Attendance
from django.contrib import messages
from django.views import View


# Admin Dashboard
@login_required
def admin_dashboard(request):
    college_count = College.objects.count()
    user_count = CustomUser.objects.count()
    student_count = Student.objects.count()
    return render(request, 'admin_dashboard.html', {
        'college_count': college_count,
        'user_count': user_count,
        'student_count': student_count
    })

# College Management
@login_required
def college_list(request):
    colleges = College.objects.all()
    return render(request, 'admin_college_list.html', {'colleges': colleges})

@login_required
def college_create(request):
    if request.method == 'POST':
        college_name = request.POST['college_name']
        College.objects.create(college_name=college_name)
        return redirect('college_list')
    return render(request, 'admin_college_form.html')

@login_required
def college_delete(request, college_id):
    college = get_object_or_404(College, id=college_id)
    college.delete()
    return redirect('college_list')



@login_required
def toggle_college(request, college_id):
    college = get_object_or_404(College, id=college_id)
    college.toggle_active()  # Toggle the active state using the model method
    return redirect('college_list')  # Redirect back to the college list


# User Management
@login_required
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'admin_user_list.html', {'users': users})

@login_required
def user_create(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        college_id = request.POST['college']
        phone = request.POST['phone']
        college = get_object_or_404(College, id=college_id)
        CustomUser.objects.create_user(phone = phone, username=username, email=email, password=password, college=college)
        return redirect('user_list')
    colleges = College.objects.all()
    return render(request, 'admin_user_form.html', {'colleges': colleges})

@login_required
def user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect('user_list')



@login_required
def user_update(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        college_id = request.POST.get("college")
        user.college = get_object_or_404(College, id=college_id) if college_id else None
        user.save()
        messages.success(request, "User updated successfully!")
        return redirect("user_list")
    colleges = College.objects.all()
    return render(request, "admin_user_update.html", {"user": user, "colleges": colleges})



# Student Management
@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, 'admin_student_list.html', {'students': students})

@login_required
def student_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        roll_no = request.POST['roll_no']
        college_id = request.POST['college']
        college = get_object_or_404(College, id=college_id)
        
        # Student create ho raha hai, par Attendance abhi create nahi hoga
        student = Student.objects.create(name=name, roll_no=roll_no, college=college, approval=2)

        return redirect('student_list')
    
    colleges = College.objects.all()
    return render(request, 'admin_student_form.html', {'colleges': colleges})

@login_required
def student_delete(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('student_list')

@login_required
def student_update(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        # Update basic fields
        student.name = request.POST.get("name")
        student.roll_no = request.POST.get("roll_no")
        student.event = request.POST.get("event")
        student.type_of_visitor = request.POST.get("type_of_visitor")
        college_id = request.POST.get("college")
        student.college = get_object_or_404(College, id=college_id)
        
        
        # Update attendance: if a status is provided, update or create the attendance record.
        new_attendance_status = request.POST.get("attendance_status")
        if new_attendance_status:
            if student.attendence:
                student.attendence.status = new_attendance_status
                student.attendence.save()
            else:
                attendance = Attendance.objects.create(user=student, status=new_attendance_status)
                student.attendence = attendance
        
        student.save()
        return redirect("student_list")
    else:
        colleges = College.objects.all()
        attendance_choices = [('Present', 'Present'), ('Absent', 'Absent'), ('Pending', 'Pending')]
        return render(request, "admin_student_update.html", {
            "student": student,
            "colleges": colleges,
            "attendance_choices": attendance_choices
        })



@login_required
def print_students(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_students')
        if not selected_ids:
            messages.error(request, "No student is selected!")
            return redirect('student_list')
        students = Student.objects.filter(id__in=selected_ids)
        return render(request, 'print_students.html', {'students': students})
    else:
        return redirect('student_list')


class admin_login(View):
    def get(self, request):
        # If the user is already authenticated, redirect them to the dashboard.
        if request.user.is_authenticated:
            return redirect('admin_dashboard')
        return render(request, 'admin_login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if the user has admin privileges (staff status) before allowing access.
            if not user.is_staff:
                messages.error(request, "User is not authorized to access the admin panel.")
                return render(request, 'admin_login.html')
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'admin_login.html')

@login_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')
