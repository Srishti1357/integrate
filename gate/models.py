from django.db import models


# class Visitor(models.Model):
#     name = models.CharField(max_length=100)
#     roll_number = models.CharField(max_length=20, unique=True)
    
#     def __str__(self):
#         return self.name

class Attendance(models.Model):
    user = models.ForeignKey("collegeApp.Student", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Pending', 'Pending')])
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.status}"