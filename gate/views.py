from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Attendance
from collegeApp.models import Student
from .serializers import UserSerializer, AttendanceSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from datetime import datetime

# def index(request):
#     today = datetime.now().date()
#     students_today = Student.objects.filter(datetime__date=today)  # Filter students by today's date
    
#     return render(request, 'index_gate.html', {'users': students_today})

def index(request):
    today = datetime.now().date()
    
    # Fetch only approved students (approval = 1)
    students_today = Student.objects.filter(datetime__date=today, approval=1)  
    
    return render(request, 'index_gate.html', {'users': students_today})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
    print(f"Permissions: {request.user.get_all_permissions()}")


    if not request.user.has_perm('gate.can_mark_attendance'):
        return Response({'error': 'You do not have permission to mark attendance.'}, status=status.HTTP_403_FORBIDDEN)

    roll_no = request.data.get('roll_no')
    status_value = request.data.get('status',2)

    if not roll_no or status_value not in [0,1,2]:
        return Response({'error': 'Missing roll_no or status'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(Student, roll_no=roll_no)

    # Update or create attendance record
    attendance, created = Attendance.objects.update_or_create(
        user=user,
        defaults={'status': status_value}
    )

    serializer = AttendanceSerializer(attendance)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def qr(request):
    return render(request, 'qr.html')



@api_view(['GET'])
def get_attendance(request, roll_no):
    user = get_object_or_404(Student, roll_no=roll_no)
    attendance = Attendance.objects.filter(student=user).first()

    if attendance:
        return Response({'status': attendance.status}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 2}, status=status.HTTP_200_OK)


