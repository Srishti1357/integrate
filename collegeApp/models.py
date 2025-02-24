from django.db import models
# from adminApp.models import College

class Visitor(models.Model):
    APPROVAL_CHOICES = [
        (0, "Rejected"),
        (1, "Accepted"),
        (2, "Pending"),
    ]
    
    id = models.AutoField(primary_key=True)
    roll_no = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    event = models.CharField(max_length=100)
    visitor_type = models.CharField(max_length=50)
    college_name = models.ForeignKey("adminApp.College", on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    approval = models.IntegerField(choices=APPROVAL_CHOICES, default=2)
    attendence = models.ForeignKey("gate.Attendance", on_delete=models.CASCADE, null=True, blank=True)

    def approval_status(self):
        return dict(self.APPROVAL_CHOICES).get(self.approval, "Unknown")


