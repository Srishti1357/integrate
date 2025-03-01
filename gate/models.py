from django.db import models


class Attendance(models.Model):
    
    student = models.ForeignKey("collegeApp.Student", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Pending', 'Pending')],
        default='Pending'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.status}"