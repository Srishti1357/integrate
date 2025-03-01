# from collegeApp.models import Student, CustomUser
from django.db import models
# from django.contrib import admin
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from django.contrib.admin import SimpleListFilter
# from django.contrib.auth.admin import UserAdmin

class College(models.Model):
    college_name = models.CharField(max_length=255, unique=True)  # Ensure unique names
    active = models.BooleanField(default=False)  # Use BooleanField for active status

    def toggle_active(self):
        """Toggle active status between True and False."""
        self.active = not self.active
        self.save()
    
    def save(self, *args, **kwargs):
        if self.active:  # If setting this college to active
            # Deactivate all other colleges
            College.objects.exclude(id=self.id).update(active=False)
        super().save(*args, **kwargs)  # Save the current instance

    def __str__(self):
        return f"{self.college_name} ({'Active' if self.active else 'Disabled'})"
