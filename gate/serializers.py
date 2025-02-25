from rest_framework import serializers
from .models import  Attendance
from collegeApp.models import Student

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'roll_number']

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['user', 'status', 'timestamp']