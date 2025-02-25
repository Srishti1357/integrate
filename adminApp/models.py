from collegeApp.models import Student, CustomUser
from django.db import models
from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin

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

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('college_name', 'active')
    list_editable = ('active',)
    search_fields = ('college_name',)
    list_filter = ('active',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):  
    list_display = ('username', 'email', 'college', 'is_staff', 'is_active')
    list_filter = ('college', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'college')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'college', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('username', 'email', 'college')
    ordering = ('username',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_no', 'name', 'college','attendence', 'datetime')
    search_fields = ('name', 'college')
    actions = ['print_students']  # Add the custom action here

    def print_students(self, request, queryset):
        """Custom action to generate a printable page."""
        # Render the printable page with the selected students
        html = render_to_string('print_students.html', {'students': queryset})

        # Create an HttpResponse with the HTML content and add JavaScript to trigger print
        response = HttpResponse(html)
        response['Content-Type'] = 'text/html'

        # Include JavaScript to trigger the print dialog
        response.write("""
            <script type="text/javascript">
                window.onload = function() {
                    window.print();
                }
            </script>
        """)

        return response

    print_students.short_description = "Print selected students"