from django.db import models
from collegeApp.models import Student
from django.utils.timezone import now

# Create your models here.
class StudentDetails(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='details')
    detail_timestamp = models.DateTimeField(auto_now_add=now)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Details for {self.student.name} at {self.detail_timestamp.strftime('%Y-%m-%d %H:%M:%S')}" 