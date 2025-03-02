from django.db import models

class Attendance(models.Model):
    student = models.ForeignKey(
        "collegeApp.Student", 
        on_delete=models.CASCADE, 
        related_name="attendances",
        null=True, blank=True
    )
    status_choices = [
    (0, 'Present'),
    (1, 'Absent'),
    (2, 'Pending'),  # Default
    ]
    status = models.IntegerField(choices=status_choices, default=2) 
    timestamp = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        permissions = [
            ("can_mark_attendance", "Can mark attendance")
        ]
    
    def __str__(self):
        return f"{self.student.name} - {self.get_status_display()}"
