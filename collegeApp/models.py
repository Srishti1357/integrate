
# from django.db import models  # ✅ Import models

# from django.contrib.auth.models import AbstractUser
# from django.core.validators import RegexValidator

# class CustomUser(AbstractUser):  # Extending Django's User model
#     college = models.ForeignKey("adminApp.College", on_delete=models.CASCADE, null=True, blank=True)
#     phone = models.CharField(
#         max_length=10,
#         unique=True,
#         validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10-digit phone number.")]
#     )

#     class Meta:
#         swappable = "AUTH_USER_MODEL"  # Ensures Django recognizes the custom user model

#     def __str__(self):
#         return f"{self.username} ({self.college if self.college else 'No College'})"

# class Student(models.Model):
#     id = models.AutoField(primary_key=True)
#     college = models.ForeignKey(
#         "adminApp.College", 
#         on_delete=models.CASCADE, 
#         limit_choices_to={'active': True}  # Only active colleges
#     )
#     roll_no = models.CharField(max_length=20, unique=True)
#     name = models.CharField(max_length=255)
#     # event = models.CharField(max_length=255)
#     # type_of_visitor = models.CharField(max_length=255)
#     event_choices = [
#         ('industry', 'Industry Visit'),
#         ('academic', 'Academic Visit'),
#     ]
#     event = models.CharField(max_length=20, choices=event_choices)
#     visitor_choices = [
#         ('student', 'Student'),
#         ('faculty', 'Faculty'),
#     ]
#     type_of_visitor = models.CharField(max_length=20, choices=visitor_choices)
#     datetime = models.DateTimeField(auto_now_add=True)
#     approval = models.IntegerField(default=2)  # 0 = Rejected, 1 = Accepted, 2 = Pending
#     attendence = models.ForeignKey(
#         'gate.Attendance', 
#         on_delete=models.CASCADE, 
#         related_name='student_attendance',  # 👈 Add a unique related_name
#         default= 2
#     )
#     phone = models.CharField(
#         max_length=10,
#         unique=True,
#         validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10-digit phone number.")]
#     )
#     college_id_card = models.ImageField(upload_to='college_id_cards/', blank=True, null=True)
#     qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

#     def __str__(self):
#         return self.name




from django.db import models  
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid

class CustomUser(AbstractUser):  
    college = models.ForeignKey("adminApp.College", on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10-digit phone number.")]
    )

    class Meta:
        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return f"{self.username} ({self.college if self.college else 'No College'})"

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    college = models.ForeignKey(
        "adminApp.College", 
        on_delete=models.CASCADE, 
        limit_choices_to={'active': True}  
    )
    roll_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    event_choices = [
        ('industry', 'Industry Visit'),
        ('academic', 'Academic Visit'),
    ]
    event = models.CharField(max_length=20, choices=event_choices)

    visitor_choices = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    ]
    type_of_visitor = models.CharField(max_length=20, choices=visitor_choices)

    datetime = models.DateTimeField(auto_now_add=True)

    approval_choices = [
        (0, 'Rejected'),
        (1, 'Accepted'),
        (2, 'Pending'),
    ]
    approval = models.IntegerField(choices=approval_choices, default=2)

    attendance = models.ForeignKey(
        'gate.Attendance', 
        on_delete=models.CASCADE, 
        related_name='student_attendance',  
        null=True, blank=True
    )

    phone = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10-digit phone number.")]
    )

    college_id_card = models.ImageField(upload_to='college_id_cards/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.name
